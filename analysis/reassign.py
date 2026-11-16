"""Re-test existing key entries that the fit-half decrypts almost never reproduce. Fit half only.

For a number (8+ fit-half uses) whose value is reproduced whole at under half the rate of the median
established entry, try every other value: the key's own letters and
syllables, umlaut spellings, and for the word and name lists the words that sort into its alphabetical
slot. A new value must be reproduced at least at the median rate and raise the whole fit-half score. The test half and its shuffled control are scored once, after all choices.

  python3 analysis/reassign.py KEY.json   # -> data/key_reassign.json, data/reassign_changes.tsv
"""
import collections, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as P
import order
import p5
from common import norm


def candidates(n, key, vocab, anc):
    pool = {norm(v) for v in key.values() if norm(v) and len(norm(v)) <= 3}  # letters and syllables
    v = norm(key.get(n, ""))
    pool |= {v.replace("oe", "o"), v.replace("ue", "u"), v.replace("ae", "a")}
    for lo, hi in order.LISTS:
        if lo <= int(n) <= hi:
            a, b, _, _ = order.window(int(n), anc[(lo, hi)])
            pool |= {w for w in vocab if a < w < b}
    pool.discard(v)
    pool.discard("")
    return sorted(pool)


def main(path, min_n=8, rounds=2):
    key = p5.load_key(path)
    lines = p5.load_lines()
    pairs = p5.gloss_pairs(lines)
    fit = [p for p in pairs if p5.fold(p["half"]) == "fit"]
    test = [p for p in pairs if p5.fold(p["half"]) == "test"]
    vocab = order.vocabulary(lines, fit)
    anc = {(lo, hi): order.anchors(key, lo, hi) for lo, hi in order.LISTS}
    new, log = dict(key), []
    ref = order.reference(key, fit)
    max_cov = ref / 2
    print("reference coverage %.2f: re-test entries under %.2f" % (ref, max_cov))
    for r in range(rounds):
        changed = 0
        uses = collections.Counter(x for p in fit for x in p["nums"])
        todo = [n for n in new if n.isdigit() and uses[n] >= min_n]
        todo = [n for n in todo if order.covered(new, [p for p in fit if n in p["nums"]], n) < max_cov]
        whole = p5.gloss_score(new, fit)
        for n in sorted(todo, key=lambda x: -uses[x]):
            mine = [p for p in fit if n in p["nums"]]
            old = new[n]
            c0 = order.covered(new, mine, n)
            best, bc, bl = None, c0, p5.gloss_score(new, mine)
            for w in candidates(n, new, vocab, anc):
                new[n] = w
                c = order.covered(new, mine, n)
                if c >= ref:
                    l = p5.gloss_score(new, mine)
                    if l > bl:
                        best, bc, bl = w, c, l
            new[n] = old
            if best:
                new[n] = best
                s = p5.gloss_score(new, fit)
                if s > whole:
                    log.append((r, n, old, best, uses[n], round(c0, 2), round(bc, 2), round(whole, 4), round(s, 4)))
                    whole, changed = s, changed + 1
                else:
                    new[n] = old
        print("round %d: %d entries re-assigned" % (r, changed), flush=True)
        if not changed:
            break
    rng = random.Random(5)
    def rep(name, k):
        ctl = [p5.gloss_score(p5.shuffled(k, rng), test) for _ in range(200)]
        print("%-22s fit %.3f | test %d decrypts %.3f | shuffled mean %.3f max %.3f" % (
            name, p5.gloss_score(k, fit), len(test), p5.gloss_score(k, test), sum(ctl) / len(ctl), max(ctl)))
    rep(os.path.basename(path), key)
    rep("+ re-assigned", new)
    json.dump(dict(sorted(new.items(), key=lambda kv: int(kv[0])),
                   _source="%s + entries re-assigned on the fit half, analysis/reassign.py" % os.path.basename(path)),
              open(os.path.join(P.D, "key_reassign.json"), "w"), ensure_ascii=False, indent=0)
    with open(os.path.join(P.D, "reassign_changes.tsv"), "w") as o:
        o.write("round\tnumber\told\tnew\tfit_uses\tcovered_old\tcovered_new\tfit_before\tfit_after\n")
        for row in log:
            o.write("\t".join(map(str, row)) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
