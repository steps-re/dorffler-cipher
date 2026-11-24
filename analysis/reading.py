"""Readable decode and overview with the ORIGINAL 1680s key, on the key-guided re-read reading.

  python3 analysis/reading.py prep      # data/reading_original/p5_decoded.txt (nulls dropped)
  CIPHER_DATA=data/reading_original python3 analysis/render.py   # model reading -> data/reading_original/reading.jsonl
  python3 analysis/reading.py md        # results/reading.md
  python3 analysis/reading.py overview  # results/overview.md (one model call over the English summaries)
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
WORK = os.path.join(REPO, "data", "reading_original")
SRC = os.path.join(REPO, "data", "reread_keyguided", "p5_lines.jsonl")
os.environ["CIPHER_DATA"] = WORK
sys.path.insert(0, HERE)
import p5  # noqa: E402
from original_key import is_null  # noqa: E402


def prep():
    os.makedirs(WORK, exist_ok=True)
    shutil.copy(SRC, os.path.join(WORK, "p5_lines.jsonl"))
    key = p5.load_key(os.path.join(REPO, "data", "key_original.json"))
    out = os.path.join(WORK, "p5_decoded.txt")
    with open(out, "w") as o:
        half = None
        for r in p5.load_lines():
            if r["half"] != half:
                half = r["half"]
                o.write("\n== %s\n" % half)
            if r["tag"] == "G":
                o.write("   G: %s\n" % r["text"]); continue
            parts = []
            for kind, v in p5.tokens(r["text"]):
                if kind == "w":
                    parts.append(v)
                elif not (v.isdigit() and is_null(v)):
                    parts.append("[" + key.get(v, "#" + v) + "]")
            o.write(" ".join(parts) + "\n")
    print("->", out)


def half_label(h):
    vol, page = h.split("/")
    side = {"L": "left", "R": "right"}[page[-1]]
    return "%s, image %d, %s half" % (vol.replace("dorffler-", ""), int(page[1:5]), side)


def records():
    recs = {}
    for l in open(os.path.join(WORK, "reading.jsonl")):
        r = json.loads(l)
        if "error" not in r:
            recs[r["half"]] = r
    return [recs[h] for h in sorted(recs)]


def render_halves():
    import render
    return render.halves()


def md():
    recs = records()
    out = os.path.join(REPO, "results", "reading.md")
    with open(out, "w") as o:
        o.write("# Dörffler despatches: readable decode\n")
        o.write("Model-made reading of the mechanical decode with the original 1680s key, on the key-guided re-read "
                "reading (`data/reread_keyguided/p5_lines.jsonl`), one half-page at a time (see METHOD.md, Step 5). "
                "Coded passages in {braces}, doubtful letters in {?...?}, unknown numbers as {#NNN}. Nulls are left out. "
                "Check anything that matters against `results/decoded_original_key.txt` and the page image "
                "(Riksarkivet SE/RA/2115/I/19/<volume>, image number = page number).\n")
        done = {r["half"] for r in recs}
        missing = [h for h, t in render_halves() if "[" in t and h not in done]
        if missing:
            o.write("\nNo model returned a reading for: %s. Their decode is in `results/decoded_original_key.txt`.\n"
                    % ", ".join(half_label(h) for h in missing))
        for r in recs:
            o.write("\n## %s\n_Summary (%s):_ %s\n\n%s\n" % (half_label(r["half"]), r["model"].split("/")[-1],
                                                            r["english"].strip(), r["german"].strip()))
    print("->", out, len(recs), "half-pages")


OVERVIEW_PROMPT = """Below are one-line English summaries of decoded cipher passages from the despatches of Simon
Dörffler, Swedish resident at the Polish court, to King Charles XI, 1682-1690, Riksarkivet volumes 19/100-19/103.
Each line starts with its reference (volume and page). Write an overview of what the coded passages are about:
one opening paragraph, then one paragraph per volume, in plain English. Every claim must come from the summaries,
and each sentence that states a fact ends with 1-4 references in parentheses in the form (19/100 p0028). Do not
use em dashes or semicolons. Do not mention summaries, models or decoding quality. Skip summaries that say a page
is blank, a fragment or unreadable. Output only the overview text.

"""


def overview():
    lines = []
    for r in records():
        vol, page = r["half"].split("/")
        lines.append("%s %s: %s" % (vol.replace("dorffler-", ""), page[:5], r["english"].strip()))
    res = subprocess.run(["llm", "-n", "-m", "vertex/gemini-4-argon", "-o", "thinking_budget", "8000", "-o", "max_output_tokens", "32000",
                          OVERVIEW_PROMPT + "\n".join(lines)], capture_output=True, text=True, timeout=900,
                         stdin=subprocess.DEVNULL)
    text = res.stdout.strip()
    if len(text) < 1500:
        sys.exit("overview too short or failed: " + (res.stdout + res.stderr)[-500:])
    out = os.path.join(REPO, "results", "overview.md")
    open(out, "w").write(text + "\n")
    print("->", out, len(text), "chars")


if __name__ == "__main__":
    {"prep": prep, "md": md, "overview": overview}[sys.argv[1]]()
