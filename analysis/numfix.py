"""Key-guided re-read of suspect cipher numbers, scored as an honest test against the clerk's decryptions.

The original 1680s key (data/key_original.json) is settled and is not changed here. Pipeline:

  detect   NO clerk decryptions (G lines) are read. For every cipher number, generate visually confusable
           alternatives that are keys or nulls of the original key, score the decoded text of a window of
           +-4 numbers under the 17th-century letter model, rank by gain.        -> suspects.jsonl
  locate   find the full-resolution strip that holds each suspect line and cut it.  -> located.json, crops/
  ask      (run on the VM) show the strip to the model, blind to key and decryptions: option A / option B
           (current vs alternative, order randomised) / other. Asked twice with the order swapped.
                                                                                  -> answers.jsonl
  apply    change a number only where both answers pick the same alternative.      -> p5_lines.jsonl
  score    original_key.py-style scores for before / after, plus the falsification controls.

All files live in --work (default data/reread_keyguided). Python 3, Pillow for `locate`.
"""
import argparse, collections, concurrent.futures as cf, fcntl, json, os, random, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.dirname(HERE)
os.environ.setdefault("CIPHER_DATA", os.path.join(REPO, "data"))
import common as P
import p5
from common import norm

HOME = os.path.expanduser("~")
SRC = os.environ.get("NUMFIX_SRC") or HOME + "/code/steps/cyphersolver/research/dudout_dorffler1773/german2026/transcription"
LM_PATH = os.environ.get("NUMFIX_LM") or HOME + "/code/steps/cipher-solutions/data/lm6.json"
HALVES = os.environ.get("CIPHER_HALVES") or HOME + "/code/steps/cipher-solutions/data/halves"
KEY_PATH = os.path.join(REPO, "data", "key_original.json")
WORK = os.path.join(REPO, "data", "reread_keyguided")
MODEL = "vertex/gemini-4-argon"

CONF = [("8", "0"), ("3", "8"), ("1", "7"), ("5", "6"), ("4", "9"), ("2", "7"), ("3", "5")]
CONFUSE = collections.defaultdict(set)
for _a, _b in CONF:
    CONFUSE[_a].add(_b); CONFUSE[_b].add(_a)
NULLS = set(range(1, 14)) | {155}
WIN = 4
MAX_SUSPECTS = 2500


def is_null(n):
    return n.isdigit() and (int(n) in NULLS or int(n) >= 349)


def load_key():
    k = p5.load_key(KEY_PATH)
    if k.get("344", "").endswith("?"):
        k.pop("344")
    return k


def valid(n, key):
    return n.isdigit() and not n.startswith("0") and (n in key or is_null(n))


def alts_of(n, key):
    """Visually confusable readings of n that are keys or nulls. Returns {alt: kind}."""
    n = n.replace('"', "")
    out = {}

    def add(a, kind):
        if a != n and valid(a, key) and a not in out:
            out[a] = kind
    for i, c in enumerate(n):
        if c == "?":
            for d in "0123456789":
                add(n[:i] + d + n[i + 1:], "unreadable")
        else:
            for d in CONFUSE.get(c, ()):
                add(n[:i] + d + n[i + 1:], "sub %s>%s" % (c, d))   # reader wrote c, alternative is d
        if len(n) > 1:
            add(n[:i] + n[i + 1:], "drop digit")                   # reader added a digit
    for i in range(len(n) + 1):
        for d in "0123456789":
            add(n[:i] + d + n[i:], "add digit")                    # reader dropped a digit
    return out


# ---------- reading ----------

def load_reading(path):
    return [json.loads(l) for l in open(path)]


NUMRE = re.compile(r"\d[\d?\"]*")


def num_spans(text):
    """Character spans of the cipher numbers in a line, in the same order as p5.nums_of."""
    return [(m.start(), m.end()) for m in NUMRE.finditer(text)]


def check_spans(lines):
    for r in lines:
        if r["tag"] == "L":
            assert len(num_spans(r["text"])) == len(p5.nums_of(r)), r


def edit_text(t, edits):
    """edits: [(token index, new value)]; keeps a trailing quote mark."""
    sp = num_spans(t)
    for j, v in sorted(edits, reverse=True):
        x, y = sp[j]
        t = t[:x] + v + ('"' if t[x:y].endswith('"') else "") + t[y:]
    return t


def piece(key, n):
    n = n.replace('"', "")
    return norm(key.get(n, "")) if not is_null(n) else ""


def stream_of(lines, ixs):
    """Tokens of the L lines of one half in order: (line_pos, kind, value, ntok_in_line)."""
    out = []
    for lp in ixs:
        r = lines[lp]
        if r["tag"] != "L":
            continue
        j = 0
        for kind, v in p5.tokens(r["text"]):
            out.append((lp, kind, v, j if kind == "n" else None))
            if kind == "n":
                j += 1
    return out


def decode_tokens(toks, key):
    return "".join(norm(v) if k == "w" else piece(key, v) for _, k, v, _ in toks)


def detect(a):
    import lm as LMmod
    os.makedirs(a.work, exist_ok=True)
    lines = load_reading(os.path.join(SRC, "p5_lines.jsonl"))
    check_spans(lines)
    key = load_key()
    lm = LMmod.LM(LM_PATH)
    by_half = collections.defaultdict(list)
    for i, r in enumerate(lines):
        by_half[r["half"]].append(i)
    # length correction: mean nats per letter of the current decoding (no decryptions involved)
    tot = n = 0
    for h, ix in list(by_half.items())[::3]:
        t = decode_tokens(stream_of(lines, ix), key)
        tot += lm.logp(t); n += len(t)
    lam = -tot / n
    print("lambda (nats/letter) %.3f from %d letters" % (lam, n), flush=True)
    sc = lambda t: lm.logp(t) + lam * len(t)
    sus, nnum, ncand = [], 0, 0
    t0 = time.time()
    for hi_, (h, ix) in enumerate(sorted(by_half.items())):
        st = stream_of(lines, ix)
        npos = [k for k, t in enumerate(st) if t[1] == "n"]
        for a_, k in enumerate(npos):
            lp, _, cur, j = st[k]
            nnum += 1
            lo = npos[max(0, a_ - WIN)]
            hi = npos[min(len(npos) - 1, a_ + WIN)]
            before = decode_tokens(st[lo:k], key)
            after = decode_tokens(st[k + 1:hi + 1], key)
            base = sc(before + piece(key, cur) + after)
            res = []
            for alt, kind in alts_of(cur, key).items():
                ncand += 1
                res.append((sc(before + piece(key, alt) + after) - base, alt, kind))
            if not res:
                continue
            res.sort(reverse=True)
            g, alt, kind = res[0]
            if g > 0:
                sus.append({"half": h, "line": lp, "tok": j, "cur": cur.replace('"', ""), "alt": alt, "kind": kind,
                            "gain": round(g, 3), "others": [[round(x[0], 3), x[1]] for x in res[1:3]]})
        if hi_ % 30 == 0:
            print(hi_, "halves,", nnum, "numbers,", len(sus), "suspects, %.0fs" % (time.time() - t0), flush=True)
    sus.sort(key=lambda s: -s["gain"])
    print("numbers %d, candidate alternatives %d, numbers with a positive-gain alternative %d" % (nnum, ncand, len(sus)))
    kept = sus[:MAX_SUSPECTS]
    for k, s in enumerate(kept):
        s["id"] = "s%04d" % k
    with open(os.path.join(a.work, "suspects.jsonl"), "w") as o:
        for s in kept:
            o.write(json.dumps(s, ensure_ascii=False) + "\n")
    json.dump({"lambda": lam, "numbers": nnum, "candidates": ncand, "positive_gain": len(sus), "kept": len(kept),
               "min_gain_kept": kept[-1]["gain"]}, open(os.path.join(a.work, "detect_summary.json"), "w"))
    print("kept %d, min gain %.2f -> suspects.jsonl" % (len(kept), kept[-1]["gain"]))
    print("kinds:", collections.Counter(s["kind"] for s in kept).most_common(14))


# ---------- locate ----------

def strip_ys(h, height, overlap):
    H = int(round(height * h)) if height < 1 else int(height)
    O = int(round(overlap * h)) if overlap < 1 else int(overlap)
    ys, y = [], 0
    while True:
        if y + H >= h:
            ys.append(max(0, h - H)); break
        ys.append(y); y += H - O
    return ys, H


def pool():
    """half -> list of (source, height, overlap, [strip texts]). 19/102 halves re-read from a standard crop
    (strips_recrop) use only that read: the older reads of them came from offset crops."""
    out = collections.defaultdict(list)
    files = [("recrop", os.path.join(SRC, "strips_recrop_19-102.jsonl")),
             ("full", os.path.join(REPO, "data", "strips_full.jsonl")),
             ("retry", os.path.join(REPO, "data", "strips_retry.jsonl"))]
    recrop = set()
    for name, f in files:
        if not os.path.exists(f):
            continue
        for l in open(f):
            r = json.loads(l)
            if "error" in r or "raw" not in r:
                continue
            if name == "recrop":
                recrop.add(r["half"])
            elif r["half"] in recrop:
                continue
            out[r["half"]].append((name, r["height"], r["overlap"], r["raw"]))
    return out


def locate(a):
    from PIL import Image
    lines = load_reading(os.path.join(SRC, "p5_lines.jsonl"))
    sus = [json.loads(l) for l in open(os.path.join(a.work, "suspects.jsonl"))]
    pl = pool()
    crops = os.path.join(a.work, "crops")
    os.makedirs(crops, exist_ok=True)
    sizes = {}
    out, miss = [], collections.Counter()
    for s in sus:
        r = lines[s["line"]]
        nums = [x.replace('"', "") for x in p5.nums_of(r)]
        best = None
        for src, ht, ov, raw in pl.get(s["half"], []):
            for k, txt in enumerate(raw):
                pl_ = p5.parse(txt)
                for pos, ln in enumerate(pl_):
                    if ln["tag"] != "L":
                        continue
                    ns = [x.replace('"', "") for x in p5.nums_of(ln)]
                    if len(ns) != len(nums):
                        continue
                    q = sum(x == y for x, y in zip(ns, nums)) / max(len(nums), 1)
                    if q < 0.85 or ns[s["tok"]] != s["cur"]:
                        continue
                    centre = min(pos, len(pl_) - 1 - pos)
                    lord = sum(1 for x in pl_[:pos + 1] if x["tag"] == "L")
                    cand = (q, centre, src, ht, ov, k, pos, lord)
                    if best is None or cand[:2] > best[:2]:
                        best = cand
        if best is None:
            miss["no strip with this line" if s["half"] in pl else "no strip read for this half"] += 1
            out.append(dict(s, located=False))
            continue
        q, centre, src, ht, ov, k, pos, lord = best
        img = os.path.join(HALVES, s["half"] + ".jpg")
        if img not in sizes:
            sizes[img] = Image.open(img).size
        w, h = sizes[img]
        ys, H = strip_ys(h, ht, ov)
        if k >= len(ys):
            miss["strip index outside geometry"] += 1
            out.append(dict(s, located=False)); continue
        cp = os.path.join(crops, "%s_%s_%d_%d.jpg" % (s["half"].replace("/", "_"), src, H, k))
        if not os.path.exists(cp):
            Image.open(img).crop((0, ys[k], w, min(h, ys[k] + H))).save(cp, quality=95)
        out.append(dict(s, located=True, crop=os.path.relpath(cp, a.work), strip=[src, ht, ov, k], line_ordinal=lord,
                        match=round(q, 2), nums=nums))
    json.dump(out, open(os.path.join(a.work, "located.json"), "w"), ensure_ascii=False)
    print("located %d of %d; misses %s; crops %d" % (sum(o["located"] for o in out), len(out), dict(miss), len(os.listdir(crops))))


# ---------- ask (runs on the VM) ----------

PROMPT = """This image is a horizontal strip cut from a page of a 1680s German diplomatic despatch. Some lines contain a numeric cipher: whole numbers separated by dots. Small lettering written in the gaps between lines is a later hand and is not a line of the despatch.

Look at the manuscript line that is about number {ord} among the lines of text in the strip, counted from the top (a first transcription may be off by one or two lines, so find the line that carries the cipher numbers listed here). A first, imperfect transcription gave these numbers for that line, left to right:
{listing}

Look only at number {t} of that line, marked with >>. The transcription gave "{cur}". Which is actually written there?
A: {A}
B: {B}
C: neither. Write exactly the digits you see.

Never guess a digit from sense. Answer with one line of JSON only: {{"answer": "A" or "B" or "C", "digits": "<the digits, only if answer is C, else empty>"}}"""


def make_prompt(s, order):
    listing = "  ".join((">>" if i == s["tok"] else "") + "%d. %s" % (i + 1, n) for i, n in enumerate(s["nums"]))
    A, B = (s["cur"], s["alt"]) if order == 0 else (s["alt"], s["cur"])
    return PROMPT.format(ord=s["line_ordinal"], listing=listing, t=s["tok"] + 1, cur=s["cur"], A=A, B=B)


def parse_answer(text, s, order):
    m = re.search(r"\{.*?\}", text or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None
    a = str(d.get("answer", "")).strip().upper()[:1]
    A, B = (s["cur"], s["alt"]) if order == 0 else (s["alt"], s["cur"])
    if a == "A":
        return A
    if a == "B":
        return B
    if a == "C":
        return "other:" + re.sub(r"[^0-9?]", "", str(d.get("digits", "")))
    return None


MAX_CALLS = int(os.environ.get("NUMFIX_MAX_CALLS", "5500"))


def call(img, prompt):
    try:
        r = subprocess.run(["llm", "-n", "-m", MODEL, "-o", "tier", "standard", "-a", img, prompt], capture_output=True,
                           text=True, timeout=120, stdin=subprocess.DEVNULL)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip(), None
        return None, r.stderr[-200:] or "empty output"
    except Exception as e:
        return None, str(e)[:200]


def ask(a):
    os.makedirs(a.work, exist_ok=True)
    lock = open(os.path.join(a.work, "answers.lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        raise SystemExit("another copy holds the lock")
    sus = [s for s in json.load(open(os.path.join(a.work, "located.json"))) if s["located"]]
    if a.only:
        ids = {l.strip() for l in open(a.only) if l.strip()}
        sus = [s for s in sus if s["id"] in ids]
    out_path = os.path.join(a.work, "answers.jsonl")
    done, tries, prior_calls = set(), collections.Counter(), 0
    if os.path.exists(out_path):
        for l in open(out_path):
            r = json.loads(l)
            prior_calls += 1
            if "error" in r:
                tries[(r["id"], r["order"])] += 1
            else:
                done.add((r["id"], r["order"]))
    jobs = [(s, o) for s in sus for o in (0, 1) if (s["id"], o) not in done and tries[(s["id"], o)] < 3]
    random.Random(5).shuffle(jobs)
    budget = MAX_CALLS - prior_calls
    print("%d jobs (%d prior calls logged, budget %d left), up to %d workers" % (len(jobs), prior_calls, budget, a.workers), flush=True)
    jobs = jobs[:max(budget, 0)]
    t0, n, bad = time.time(), 0, 0

    def one(job):
        s, o = job
        txt, err = call(os.path.join(a.work, s["crop"]), make_prompt(s, o))
        rec = {"id": s["id"], "order": o, "t": round(time.time())}
        if txt is None:
            return dict(rec, error=err)
        val = parse_answer(txt, s, o)
        if val is None:
            return dict(rec, error="unparseable: " + txt[:120])
        return dict(rec, value=val, raw=txt[:200])

    # continuous pool: no worker waits for a straggler. Workers start staggered (worker k starts after 8*k
    # finished calls), so the request rate ramps up rather than starting at full speed.
    import threading, queue
    q = queue.Queue()
    for j in jobs:
        q.put(j)
    lk = threading.Lock()
    st = {"n": 0, "bad": 0}
    o = open(out_path, "a")
    stop = threading.Event()

    def worker(k):
        while st["n"] < 8 * k and not stop.is_set() and not q.empty():
            time.sleep(1)
        while not stop.is_set():
            try:
                job = q.get_nowait()
            except queue.Empty:
                return
            rec = one(job)
            with lk:
                o.write(json.dumps(rec, ensure_ascii=False) + "\n"); o.flush()
                st["n"] += 1; st["bad"] += "error" in rec
                if st["n"] == 16 and st["bad"] == 16:
                    print("ABORT: first 16 calls all failed: " + rec["error"], flush=True)
                    stop.set()
                if st["n"] % 100 == 0:
                    print("%d calls, %d errors (counted apart from progress), %.0fs" % (st["n"], st["bad"], time.time() - t0), flush=True)
    ths = [threading.Thread(target=worker, args=(k,)) for k in range(a.workers)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    o.close()
    print("finished: %d calls, %d errors, %.0fs" % (st["n"], st["bad"], time.time() - t0))


# ---------- apply ----------

def adjudicate(a):
    sus = {s["id"]: s for s in json.load(open(os.path.join(a.work, "located.json")))}
    ans = collections.defaultdict(dict)
    for l in open(os.path.join(a.work, "answers.jsonl")):
        r = json.loads(l)
        if "error" not in r:
            ans[r["id"]][r["order"]] = r["value"]
    key = load_key()
    acc, st = {}, collections.Counter()
    for sid, s in sus.items():
        if not s["located"]:
            st["failed: line not located in a strip"] += 1; continue
        d = ans.get(sid, {})
        if len(d) < 2:
            st["failed: fewer than 2 answers"] += 1; continue
        v0, v1 = d[0], d[1]
        st["both answered"] += 1
        if v0 != v1:
            st["disagree"] += 1; continue
        st["agree"] += 1
        if v0 == s["cur"]:
            st["agree: keep current"] += 1
        elif v0 == s["alt"]:
            acc[sid] = s["alt"]; st["agree: alternative"] += 1
        elif v0.startswith("other:") and valid(v0[6:], key) and v0[6:] != s["cur"]:
            acc[sid] = v0[6:]; st["agree: other (valid)"] += 1
        else:
            st["agree: other (invalid or empty)"] += 1
    return acc, st, sus


def apply_(a):
    acc, st, sus = adjudicate(a)
    lines = load_reading(os.path.join(SRC, "p5_lines.jsonl"))
    new = [dict(r) for r in lines]
    by_line = collections.defaultdict(list)
    for sid, v in acc.items():
        by_line[sus[sid]["line"]].append((sus[sid]["tok"], v))
    for lp, edits in by_line.items():
        new[lp]["text"] = edit_text(new[lp]["text"], edits)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "p5_lines.jsonl"), "w") as o:
        for r in new:
            o.write(json.dumps(r, ensure_ascii=False) + "\n")
    kinds = collections.Counter(sus[s]["kind"] if acc[s] == sus[s]["alt"] else "other (image says a different number)" for s in acc)
    json.dump({"stats": st, "accepted": acc, "kinds": kinds}, open(os.path.join(a.work, "accepted.json"), "w"), indent=0, ensure_ascii=False)
    print(dict(st)); print("accepted", len(acc)); print("kinds", kinds.most_common())


# ---------- score ----------

def subsets(pairs):
    sub = collections.OrderedDict([
        ("test half", [p for p in pairs if p5.fold(p["half"]) == "test"]),
        ("fit half", [p for p in pairs if p5.fold(p["half"]) == "fit"]),
        ("fresh lines", [p for p in pairs if p["half"].split("/")[0] not in p5.TRAIN_VOLS and p["half"][:-1] not in p5.SPENT]),
        ("all lines", pairs)])
    for v in sorted({p["half"].split("/")[0] for p in pairs}):
        sub[v] = [p for p in pairs if p["half"].startswith(v + "/")]
    return sub


def scores(lines, key, draws=0):
    res = {}
    for name, ps in subsets(p5.gloss_pairs(lines)).items():
        row = {"lines": len(ps), "letters": sum(len(p["gloss"]) for p in ps), "score": p5.gloss_score(key, ps)}
        if draws:
            rng = random.Random(7)
            sh = [p5.gloss_score(p5.shuffled(key, rng), ps) for _ in range(draws)]
            row["shuf_mean"], row["shuf_max"] = sum(sh) / draws, max(sh)
        res[name] = row
    return res


def random_edits(lines, key, n, rng):
    """n random confusable edits (same kinds as the detector) at random number positions on L lines."""
    cands = [(i, j) for i, r in enumerate(lines) if r["tag"] == "L" for j in range(len(p5.nums_of(r)))]
    chosen, edits, tries = set(), collections.defaultdict(list), 0
    while len(chosen) < n and tries < n * 50:
        tries += 1
        i, j = rng.choice(cands)
        if (i, j) in chosen:
            continue
        al = alts_of(p5.nums_of(lines[i])[j], key)
        if not al:
            continue
        chosen.add((i, j)); edits[i].append((j, rng.choice(sorted(al))))
    new = [dict(r) for r in lines]
    for i, es in edits.items():
        new[i]["text"] = edit_text(new[i]["text"], es)
    return new


def score_cmd(a):
    key = load_key()
    before = load_reading(os.path.join(SRC, "p5_lines.jsonl"))
    after = load_reading(os.path.join(a.out, "p5_lines.jsonl"))
    acc, st, sus = adjudicate(a)
    sb, sa = scores(before, key, 200), scores(after, key, 200)
    out = []

    def pr(s=""):
        print(s); out.append(s)
    pr("Score = share of the clerk's decryption letters reproduced in runs of 3+ letters, ORIGINAL 1680s key unchanged.")
    pr("Shuffled = same key with values shuffled among its numbers, 200 draws (mean/max shown for the AFTER reading).")
    pr("%-16s %6s %7s | %8s %8s %7s | %s" % ("subset", "lines", "letters", "before", "after", "change", "shuffled mean/max"))
    for name in sb:
        b, af = sb[name], sa[name]
        pr("%-16s %6d %7d | %7.2f%% %7.2f%% %+6.2f | %5.2f%% / %5.2f%%" % (
            name, af["lines"], af["letters"], 100 * b["score"], 100 * af["score"], 100 * (af["score"] - b["score"]),
            100 * af["shuf_mean"], 100 * af["shuf_max"]))
    N = len(acc)
    pr("\nAccepted changes: %d" % N)
    draws = a.control_draws
    ctl = collections.defaultdict(list)
    for d in range(draws):
        s = scores(random_edits(before, key, N, random.Random(1000 + d)), key)
        for name in ("test half", "fit half", "fresh lines"):
            ctl[name].append(s[name]["score"])
    pr("\nFALSIFICATION CONTROL: %d random confusable edits at random positions (same count as accepted), %d draws" % (N, draws))
    for name in ("test half", "fit half", "fresh lines"):
        v = ctl[name]
        pr("  %-12s before %.2f%% | random edits mean %.2f%% (min %.2f, max %.2f) | real accepted edits %.2f%%" % (
            name, 100 * sb[name]["score"], 100 * sum(v) / len(v), 100 * min(v), 100 * max(v), 100 * sa[name]["score"]))
    ok = sum(ctl["test half"]) / draws < sb["test half"]["score"]
    pr("  control %s the test-half score" % ("DROPS" if ok else "DID NOT DROP: THE MEASURE IS BROKEN OR THE EDITS ARE NOT HARMFUL"))
    # bonus: the first N language-model suspects (highest gain) applied with no image check
    lm_only = [dict(r) for r in before]
    ed = collections.defaultdict(list)
    for s in sorted(sus.values(), key=lambda s: s["id"])[:N]:
        ed[s["line"]].append((s["tok"], s["alt"]))
    for lp, es in ed.items():
        lm_only[lp]["text"] = edit_text(lm_only[lp]["text"], es)
    sl = scores(lm_only, key)
    pr("\nBONUS: the top-%d language-model suspects applied with NO image check: test half %.2f%%, fit half %.2f%%, fresh %.2f%%" % (
        N, 100 * sl["test half"]["score"], 100 * sl["fit half"]["score"], 100 * sl["fresh lines"]["score"]))
    pr("\n10 random accepted changes (decoded with the original key; letters of nulls are dropped; clerk's text not shown)")
    rng = random.Random(11)
    dec = lambda toks: "".join(piece(key, v) if k == "n" else norm(v) for k, v in toks)
    for sid in rng.sample(sorted(acc), min(10, len(acc))):
        s = sus[sid]
        t0, t1 = p5.tokens(before[s["line"]]["text"]), p5.tokens(after[s["line"]]["text"])
        ntok = [i for i, (k, _) in enumerate(t0) if k == "n"]
        lo, hi = ntok[max(0, s["tok"] - 5)], ntok[min(len(ntok) - 1, s["tok"] + 5)] + 1
        pr("  %s %s line %d: %s -> %s (%s, LM gain %.1f)" % (sid, s["half"], before[s["line"]]["i"], s["cur"], acc[sid], s["kind"], s["gain"]))
        pr("      before: %s" % dec(t0[lo:hi]))
        pr("      after : %s" % dec(t1[lo:hi]))
    open(os.path.join(a.work, "report_scores.txt"), "w").write("\n".join(out) + "\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("detect", "locate", "ask", "apply", "score"):
        s = sub.add_parser(n)
        s.add_argument("--work", default=WORK)
        s.add_argument("--out", default=WORK)
        s.add_argument("--workers", type=int, default=12)
        s.add_argument("--only", help="file of suspect ids to ask about (pilot)")
        s.add_argument("--control-draws", type=int, default=30)
    a = ap.parse_args()
    {"detect": detect, "locate": locate, "ask": ask, "apply": apply_, "score": score_cmd}[a.cmd](a)


if __name__ == "__main__":
    main()
