"""Letter-level language model of 17th-century German, to score how German a decoding reads.

Source: Deutsches Textarchiv, DTA komplett 1600-1699 (1,114 texts, CC BY-SA), md5 20347578...
Text is folded the way common.norm folds it (letters a-z only, umlauts to the base vowel, long s to s),
so a decoding and the model see the same alphabet. Spaces are dropped because the cipher marks no
word boundaries.

  python3 analysis/lm.py build      # data/dta/raw/**.xml -> data/lm6.json
  python3 analysis/lm.py score TEXT # bits per letter (lower = more German)
"""
import collections, glob, json, math, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import common as P
from common import norm

ORDER = 6
PATH = os.path.join(P.D, "lm6.json")


def corpus_text():
    for f in sorted(glob.glob(os.path.join(P.D, "dta", "raw", "**", "*.xml"), recursive=True)):
        x = open(f, encoding="utf-8", errors="ignore").read()
        x = x.split("<text", 1)[-1]
        x = re.sub(r"<(note|fw|teiHeader)[^>]*>.*?</\1>", " ", x, flags=re.S)
        x = re.sub(r"<[^>]+>", "", x).replace("ſ", "s")
        yield norm(x)


def build():
    counts = [collections.Counter() for _ in range(ORDER + 1)]
    n = 0
    for t in corpus_text():
        n += len(t)
        for k in range(1, ORDER + 1):
            c = counts[k]
            for i in range(len(t) - k + 1):
                c[t[i:i + k]] += 1
    # keep contexts seen at least twice, plenty for scoring at this corpus size
    model = {"order": ORDER, "letters": n,
             "c": {k: {g: v for g, v in counts[k].items() if v >= 2 or k == 1} for k in range(1, ORDER + 1)}}
    json.dump(model, open(PATH, "w"))
    print("letters", n, "ngrams", sum(len(v) for v in model["c"].values()), "->", PATH)


class LM:
    """Interpolated absolute-discount model; logp(text) in nats, bits per letter for reporting."""

    def __init__(self, path=PATH):
        m = json.load(open(path))
        self.k = m["order"]
        self.c = [None] + [m["c"][str(k)] for k in range(1, self.k + 1)]
        self.total = sum(self.c[1].values())
        self.ctx = [None] + [collections.Counter() for _ in range(self.k)]
        self.fan = [None] + [collections.Counter() for _ in range(self.k)]
        for k in range(2, self.k + 1):
            for g, v in self.c[k].items():
                self.ctx[k][g[:-1]] += v
                self.fan[k][g[:-1]] += 1
        self.cache = {}

    def p(self, hist, ch):
        key = (hist, ch)
        r = self.cache.get(key)
        if r is not None:
            return r
        pr = (self.c[1].get(ch, 0) + 1) / (self.total + 26)
        d = 0.75
        for k in range(2, self.k + 1):
            h = hist[-(k - 1):]
            if len(h) < k - 1:
                break
            n = self.ctx[k].get(h)
            if not n:
                break
            pr = max(self.c[k].get(h + ch, 0) - d, 0) / n + d * self.fan[k][h] / n * pr
        r = math.log(pr)
        if len(self.cache) < 2_000_000:
            self.cache[key] = r
        return r

    def logp(self, text, hist=""):
        s = 0.0
        for ch in text:
            s += self.p(hist, ch)
            hist = (hist + ch)[-(self.k - 1):]
        return s

    def bits(self, text):
        return -self.logp(text) / math.log(2) / max(len(text), 1)


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build()
    else:
        print("%.2f bits/letter" % LM().bits(norm(" ".join(sys.argv[2:]))))
