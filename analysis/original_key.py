"""Score the original 1680s key (Riksarkivet Chifferklaver vol. 3, III:20) against TABLE-C04 and our final key.

The original key is external evidence: no part of it was fitted to the decrypts, so every line is held out.
  python3 analysis/original_key.py            # scores + key diff -> results/original_key_report.txt
"""
import collections, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p5
from common import norm

KEYS = [("TABLE-C04", "data/key_c04.json"), ("final key (C04+fills)", "results/key_final.json"),
        ("ORIGINAL 1680s key", "data/key_original.json")]
NULLS = set(range(1, 14)) | {155}


def is_null(n):
    return n.isdigit() and (int(n) in NULLS or int(n) >= 349)


def main():
    lines = p5.load_lines()
    pairs = p5.gloss_pairs(lines)
    halves = sorted({r["half"] for r in lines})
    sub = {
        "all lines": pairs,
        "test half": [p for p in pairs if p5.fold(p["half"]) == "test"],
        "fit half": [p for p in pairs if p5.fold(p["half"]) == "fit"],
        "fresh lines": [p for p in pairs if p["half"].split("/")[0] not in p5.TRAIN_VOLS and p["half"][:-1] not in p5.SPENT],
    }
    for v in sorted({h.split("/")[0] for h in halves}):
        sub[v] = [p for p in pairs if p["half"].startswith(v + "/")]
    out = []
    pr = lambda s="": (print(s), out.append(s))
    keys = {name: p5.load_key(path) for name, path in KEYS}
    keys["ORIGINAL 1680s key"].pop("344", None) if keys["ORIGINAL 1680s key"].get("344", "").endswith("?") else None
    pr("Score = share of the clerk's decryption letters reproduced in runs of 3+ letters (same measure as evaluation.txt).")
    pr("Shuffled = same key, values shuffled among its numbers, 200 draws.\n")
    pr("%-16s %7s %7s | %s" % ("subset", "lines", "letters", " | ".join("%-26s" % n for n, _ in KEYS)))
    for sname, ps in sub.items():
        cells = []
        for name, _ in KEYS:
            k = keys[name]
            rng = random.Random(7)
            sh = [p5.gloss_score(p5.shuffled(k, rng), ps) for _ in range(200)]
            cells.append("%5.1f%% (shuf %4.1f, max %4.1f)" % (100 * p5.gloss_score(k, ps), 100 * sum(sh) / 200, 100 * max(sh)))
        pr("%-16s %7d %7d | %s" % (sname, len(ps), sum(len(p["gloss"]) for p in ps), " | ".join(cells)))
    # coverage
    nums = [n for r in lines if r["tag"] == "L" for n in p5.nums_of(r) if n.isdigit()]
    c = collections.Counter(nums)
    pr("\nCipher numbers in the reading: %d" % len(nums))
    for name, _ in KEYS:
        k = keys[name]
        unk = sum(v for n, v in c.items() if n not in k and not (name.startswith("ORIG") and is_null(n)))
        pr("  %-24s no value: %.1f%%" % (name, 100 * unk / len(nums)))
    nul = sum(v for n, v in c.items() if is_null(n))
    pr("  numbers the original key declares NULL (1-13, 155, 349+): %d (%.1f%%)" % (nul, 100 * nul / len(nums)))
    top = collections.Counter({n: v for n, v in c.items() if is_null(n)}).most_common(15)
    pr("  most frequent nulls: " + ", ".join("%s x%d" % t for t in top))
    # key diff
    o, c4, fk = keys["ORIGINAL 1680s key"], keys["TABLE-C04"], keys["final key (C04+fills)"]
    pr("\nEntry-by-entry: original vs C04 and vs our final key (uses = times the number occurs in the reading)")
    agree_c4 = agree_f = disagree = 0
    rows = []
    for n in sorted(set(o) | set(c4) | set(fk), key=int):
        ov = o.get(n, "NULL" if is_null(n) else "-")
        a, b = c4.get(n, "-"), fk.get(n, "-")
        same = lambda x: norm(x) == norm(ov) and x != "-"
        if same(a): agree_c4 += 1
        if same(b): agree_f += 1
        if not same(b):
            rows.append("  %4s x%-4d original=%-14s C04=%-12s final=%-12s%s" % (n, c.get(n, 0), ov, a, b,
                        "  <- our fill" if a != b else ""))
    pr("  original entries: %d | C04 matches %d | final key matches %d" % (len(o), agree_c4, agree_f))
    pr("  fills/proposals we added (C04 -> final), checked against the original:")
    for n in sorted([n for n in fk if fk.get(n) != c4.get(n)], key=int):
        pr("    %4s %-12s -> %-12s original=%-14s %s" % (n, c4.get(n, "-"), fk[n], o.get(n, "NULL" if is_null(n) else "-"),
                                                       "RIGHT" if norm(fk[n]) == norm(o.get(n, "")) else "wrong"))
    pr("  every number where our final key differs from the original:")
    out += rows; print("\n".join(rows))
    open("results/original_key_report.txt", "w").write("\n".join(out) + "\n")


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


def decode_all(out_path="results/decoded_original_key.txt"):
    """Mechanical decode of every cipher line with the original key. Nulls print as '·'; numbers the key
    lacks (none expected) as #n. Clerk's decryptions follow on G: lines."""
    key = {n: v for n, v in p5.load_key("data/key_original.json").items()}
    with open(out_path, "w") as o:
        o.write("# Decoded with the ORIGINAL key (Riksarkivet Chifferklaver vol. 3, III:20). Reading: %s/p5_lines.jsonl\n"
                % os.environ.get("CIPHER_DATA", "data"))
        half = None
        for r in p5.load_lines():
            if r["half"] != half:
                half = r["half"]; o.write("\n== %s\n" % half)
            if r["tag"] == "G":
                o.write("   G: %s\n" % r["text"]); continue
            out = []
            for kind, v in p5.tokens(r["text"]):
                if kind == "w": out.append(v)
                elif v.isdigit() and is_null(v): out.append("·")
                else: out.append("[" + key.get(v, "#" + v) + "]")
            o.write(" ".join(out) + "\n")
    print("->", out_path)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "decode":
    decode_all()
