"""Settle numbers the two readers disagree on, by looking at the image again; the key breaks ties.

For each half-page with disputes (p5_lines "alt"), one call shows the full-resolution half and lists every
disputed number with its neighbours ("... 77.53.[87 or 67].28.33 ..."). The model answers per dispute
with one of the two readings or "unsure". Unsure, failed or out-of-range answers fall back to the key:
the reading whose decoded piece scores better under the 17th-century German letter model, if it beats
the other by MARGIN nats; otherwise the primary reading stays. No decrypt (G:) line is used, so the
held-out test stays fair.

  python3 analysis/adjudicate.py look    # model answers -> data/adjudicate.jsonl (resumes)
  python3 analysis/adjudicate.py apply   # rewrite p5_lines.jsonl numbers; old copy kept as p5_lines.before_adjudication.jsonl
Done-test: every half with disputes has records for all its chunks; apply prints how each dispute was settled.
"""
import collections, concurrent.futures as cf, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as P
import p5
from common import norm

MODEL = "vertex/gemini-4-argon"
FALLBACK = "vertex/gemini-3.8-flash"
OUT = os.path.join(P.D, "adjudicate.jsonl")
CHUNK = 40
MARGIN = 2.0
PROMPT = """This image is one page-half of a 1680s German despatch with numeric cipher (numbers separated by dots).
Two readers disagreed on some numbers. For each item below, find that spot on the page (use the neighbouring
numbers to locate it) and say which reading is what is actually written. Look carefully at the digits:
common confusions are 1/7, 3/8, 0/8, 6/8, 2/7, 21/26, 87/67.
Answer only JSON: {"<id>": "<first or second reading exactly as given, or unsure>", ...}

"""


def disputes():
    by_half = collections.defaultdict(list)
    for r in p5.load_lines():
        if not r.get("alt"):
            continue
        ns = p5.nums_of(r)
        for pos, alt in r["alt"].items():
            k = int(pos)
            ctx = ".".join(ns[max(0, k - 3):k]) + ".[" + ns[k] + " or " + alt + "]." + ".".join(ns[k + 1:k + 4])
            by_half[r["half"]].append({"id": "%d_%s" % (r["i"], pos), "i": r["i"], "pos": k, "a": ns[k], "b": alt, "ctx": ctx})
    return by_half


def look():
    done = set()
    if os.path.exists(OUT):
        done = {(json.loads(l)["half"], json.loads(l)["chunk"]) for l in open(OUT) if '"error"' not in l}
    jobs = []
    for half, ds in sorted(disputes().items()):
        for c in range(0, len(ds), CHUNK):
            if (half, c) not in done:
                jobs.append((half, c, ds[c:c + CHUNK]))
    print(len(jobs), "calls to make", flush=True)

    def one(job):
        half, c, ds = job
        ms, p = half.split("/")
        img = os.path.join(P.D, "halves", ms, p + ".jpg")
        text = PROMPT + "\n".join("%s: %s   (readings: %s or %s)" % (d["id"], d["ctx"], d["a"], d["b"]) for d in ds)
        for m in (MODEL, FALLBACK):
            out, err = P.ask(m, img, text, timeout=600, tier="standard")
            hit = re.search(r"\{.*\}", out or "", re.S)
            if hit:
                try:
                    return {"half": half, "chunk": c, "model": m, "answers": json.loads(hit.group(0))}
                except Exception:
                    err = (out or "")[-200:]
        return {"half": half, "chunk": c, "error": err}

    with cf.ThreadPoolExecutor(8) as ex, open(OUT, "a") as o:
        for n, rec in enumerate(ex.map(one, jobs), 1):
            o.write(json.dumps(rec, ensure_ascii=False) + "\n"); o.flush()
            if n % 20 == 0:
                print(n, "done", flush=True)


def replace_nth_number(text, k, new):
    seen = -1
    def sub(m):
        nonlocal seen
        seen += 1
        return new + m.group(0)[len(m.group(1)):] if seen == k else m.group(0)
    return re.sub(r"(\d[\d?]*)\"?", sub, text)


def apply():
    from lm import LM
    lm = LM()
    key = p5.load_key(os.path.join(P.D, "key_final.json"))
    answers = {}
    for l in open(OUT):
        r = json.loads(l)
        for k, v in r.get("answers", {}).items():
            answers[(r["half"], k)] = str(v).strip()
    src = os.path.join(P.D, "p5_lines.jsonl")
    backup = os.path.join(P.D, "p5_lines.before_adjudication.jsonl")
    if not os.path.exists(backup):
        shutil.copy(src, backup)
    lines = [json.loads(l) for l in open(backup)]
    tally = collections.Counter()
    for r in lines:
        if not r.get("alt"):
            continue
        ns = p5.nums_of(r)
        for pos, alt in r["alt"].items():
            k = int(pos)
            a, b = ns[k], alt
            ans = answers.get((r["half"], "%d_%s" % (r["i"], pos)))
            if ans == a:
                choice, how = a, "image: first reader"
            elif ans == b:
                choice, how = b, "image: second reader"
            else:
                left = "".join(norm(key.get(x, "")) for x in ns[max(0, k - 3):k])[-5:]
                right = "".join(norm(key.get(x, "")) for x in ns[k + 1:k + 3])[:5]
                sa = lm.logp(norm(key.get(a, "")) + right, left)
                sb = lm.logp(norm(key.get(b, "")) + right, left)
                choice, how = (b, "key: second reader") if sb > sa + MARGIN else (a, "unsettled: first reader kept")
            tally[how] += 1
            if choice != a:
                r["text"] = replace_nth_number(r["text"], k, choice)
            r.setdefault("settled", {})[pos] = how
        r["alt_original"] = r.pop("alt")
    with open(src, "w") as o:
        for r in lines:
            o.write(json.dumps(r, ensure_ascii=False) + "\n")
    for k, v in tally.most_common():
        print("%-30s %d" % (k, v))


if __name__ == "__main__":
    {"look": look, "apply": apply}[sys.argv[1]]()
