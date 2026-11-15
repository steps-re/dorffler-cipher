"""Refine the codebook against the whole cipher corpus, starting from C04.

For every cipher number, in turn, try each candidate value (a letter, a two-letter syllable, a word
from 17th-century German, or nothing) at every place the number occurs, and keep the value under
which the decoded text, in its clear-German context, reads most like German. Gloss letters from the
TRAINING volume (19/102) add a bonus. Held-out decrypts are never consulted here.
A change is kept only if it gains more than MARGIN nats, so a rare number keeps its C04 value
unless the evidence is clear. Where the two readers disagreed on a number, the reading under which
the line reads better is used (alt field from p5.merge).

Score of a letter = log p(letter | 5 letters before) + BASE, BASE = the cost of an average German
letter, so a value is not rewarded just for being short.
"""
import collections, glob, json, math, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as P
import p5
from lm import LM
from common import norm

BASE = 2.8 * math.log(2)  # nats per letter of ordinary German under this model
MARGIN = 2.0
GLOSS_W = 1.5             # nats per decrypt letter matched (training volume only)
CTX = 5
OUT = os.environ.get("REFINE_OUT") or os.path.join(P.D, "key_p5.json")
VOW = "aeiouy"
CONS = "bcdfghklmnpqrstwxz"


def word_candidates(n=250):
    c = collections.Counter()
    for f in sorted(glob.glob(os.path.join(P.D, "dta", "raw", "**", "*.xml"), recursive=True))[::10]:
        x = re.sub(r"<[^>]+>", " ", open(f, encoding="utf-8", errors="ignore").read().split("<text", 1)[-1])
        c.update(w for w in (norm(t) for t in x.replace("ſ", "s").split()) if 3 <= len(w) <= 8)
    return [w for w, _ in c.most_common(n)]


def candidates(key):
    s = {""} | set(map(norm, key.values())) | set("abcdefghiklmnopqrstuvwxyz")
    s |= {c + v for c in CONS for v in VOW} | {v + c for c in CONS for v in VOW}
    s |= {"ch", "sch", "st", "ck", "ss", "tz", "en", "er", "ein", "ung", "lich", "der", "die", "das", "und"}
    s |= set(word_candidates())
    return sorted(s)


class Corpus:
    def __init__(self):
        self.lines = [r for r in p5.load_lines() if r["tag"] == "L" and p5.nums_of(r)]
        self.toks = [p5.tokens(r["text"]) for r in self.lines]
        self.choice = [dict() for _ in self.lines]  # token index -> chosen alternative reading
        self.occ = collections.defaultdict(list)    # number -> [(line, token index)]
        for li, (r, ts) in enumerate(zip(self.lines, self.toks)):
            for j, (k, v) in enumerate(ts):
                if k == "n" and v.isdigit():
                    self.occ[v].append((li, j))
                    alt = r.get("alt", {}).get(str(len([1 for kk, _ in ts[:j] if kk == "n"])))
                    if alt:
                        self.occ[alt].append((li, j))
        pairs = [p for p in p5.gloss_pairs(p5.load_lines()) if p["half"].split("/")[0] in p5.TRAIN_VOLS]
        self.train_pairs = pairs

    def number_at(self, li, j):
        return self.choice[li].get(j, self.toks[li][j][1])

    def piece(self, key, li, j):
        k, v = self.toks[li][j]
        return norm(v) if k == "w" else norm(key.get(self.number_at(li, j), ""))

    def context(self, key, li, j):
        left = ""
        jj = j - 1
        while jj >= 0 and len(left) < CTX:
            left = self.piece(key, li, jj) + left
            jj -= 1
        right = ""
        jj = j + 1
        while jj < len(self.toks[li]) and len(right) < CTX:
            right += self.piece(key, li, jj)
            jj += 1
        return left[-CTX:], right[:CTX]


def local(lm, left, val, right):
    s = lm.logp(val + right, left) + BASE * len(val)
    return s


def gloss_bonus(key, pairs, num):
    b = 0.0
    for p in pairs:
        if num in p["nums"]:
            dec = "".join(norm(key.get(n, "")) for n in p["nums"])
            b += GLOSS_W * p5.local_match(p["gloss"], dec)
    return b


def main(sweeps=4):
    t0 = time.time()
    lm = LM()
    key = p5.load_key(os.path.join(P.D, "key_c04.json"))
    C = Corpus()
    cands = candidates(key)
    gl_nums = collections.Counter(n for p in C.train_pairs for n in p["nums"])
    print("lines", len(C.lines), "numbers", len(C.occ), "candidates", len(cands), flush=True)
    log = open(os.path.join(P.D, "refine.log"), "a")
    for sweep in range(sweeps):
        changed = 0
        # 1. pick between the two readers' numbers where they disagree
        for li, r in enumerate(C.lines):
            nidx = [j for j, (k, _) in enumerate(C.toks[li]) if k == "n"]
            for pos, alt in r.get("alt", {}).items():
                j = nidx[int(pos)]
                prim = C.toks[li][j][1]
                left, right = C.context(key, li, j)
                a = local(lm, left, norm(key.get(prim, "")), right)
                b = local(lm, left, norm(key.get(alt, "")), right)
                C.choice[li][j] = alt if b > a + MARGIN else prim
        # 2. coordinate ascent over numbers, most frequent first
        order = sorted(C.occ.items(), key=lambda kv: -len(kv[1]))
        if os.environ.get("REFINE_LIMIT"):  # dry runs
            order = order[:int(os.environ["REFINE_LIMIT"])]
        for num, occ in order:
            occ = [(li, j) for li, j in occ if C.number_at(li, j) == num]
            if len(occ) < 2:
                continue
            ctxs = [C.context(key, li, j) for li, j in occ]
            cur = key.get(num, "")
            # Same-length classes from the key's structure (Dudout): within a class the language
            # model compares like with like. The open class (words, names, the rest) changes only on
            # decrypt evidence, because the model alone always prefers longer common words.
            n_int = int(num)
            if n_int <= 65:
                pool, open_class = [c for c in cands if len(c) == 1], False
            elif n_int <= 145:
                pool, open_class = [c for c in cands if len(c) == 2], False
            else:
                pool, open_class = cands, True
            if open_class and not gl_nums.get(num):
                continue
            g0 = gloss_bonus(key, C.train_pairs, num) if gl_nums.get(num) else 0.0
            def total(v):
                s = sum(local(lm, l, v, r) for l, r in ctxs)
                if gl_nums.get(num):
                    old = key.get(num)
                    key[num] = v
                    s += gloss_bonus(key, C.train_pairs, num)
                    if old is None:
                        key.pop(num)
                    else:
                        key[num] = old
                return s
            base = total(norm(cur))
            best, bv = cur, base
            for v in pool:
                if open_class:
                    old = key.get(num)
                    key[num] = v
                    g = gloss_bonus(key, C.train_pairs, num)
                    key.pop(num) if old is None else key.__setitem__(num, old)
                    if g < g0 + 3 * GLOSS_W:  # at least 3 more decrypt letters explained
                        continue
                s = total(v)
                if s > bv:
                    best, bv = v, s
            if norm(best) != norm(cur) and bv > base + MARGIN:
                print("sweep %d  %4s x%-4d %-8s -> %-8s gain %.1f" % (sweep, num, len(occ), cur or "-", best or "-", bv - base),
                      file=log, flush=True)
                key[num] = best
                changed += 1
        json.dump(dict(sorted(key.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0),
                       _source="C04 refined by analysis/refine.py, sweep %d" % sweep), open(OUT, "w"), ensure_ascii=False, indent=0)
        print("sweep", sweep, "changed", changed, "%.0f s" % (time.time() - t0), flush=True)
        if not changed:
            break


if __name__ == "__main__":
    main()
