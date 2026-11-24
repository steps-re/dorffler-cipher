"""Readable version of the mechanical decode, one page-half at a time (model-assisted, labelled as such).

Input: data/p5_decoded.txt (clear German, decoded cipher pieces in [brackets], contemporary decrypts on
G: lines). The model only segments and spells the decoded letters as words; it must not add content and
must mark doubtful stretches. Output: data/reading.jsonl {"half", "german", "english"}.
"""
import concurrent.futures as cf, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as P

MODEL = "vertex/gemini-4-argon"
OUT = os.path.join(P.D, "reading.jsonl")
PROMPT = """Below is one page-half of a despatch by Simon Dörffler, Swedish resident in Poland, to King Charles XI
(1682-1690). Ordinary German is written plainly. Passages that were in cipher appear as decoded pieces in
[brackets], one piece per cipher number; a piece written #NNN is a number whose meaning is unknown.
Lines starting "G:" are a contemporary decryption written above the cipher by a 1680s hand.

Task:
1. GERMAN: rewrite the page-half as continuous German, joining the bracketed pieces into words. Keep the old
   spelling. Use only letters that are in the pieces or the plain text. Mark every cipher passage with
   {curly braces}. Where the pieces do not make sense, write the letters as they are inside {?...?}.
   Write an unknown number as {#NNN}. You may use the G: lines only to choose word breaks, never to add
   words that the pieces do not contain. Do not add anything else.
2. ENGLISH: one or two sentences saying what this page-half is about, based on the GERMAN.
Answer as JSON: {"german": "...", "english": "..."}

"""


def halves():
    cur, buf = None, []
    for l in open(os.path.join(P.D, "p5_decoded.txt")):
        if l.startswith("== "):
            if cur:
                yield cur, "".join(buf)
            cur, buf = l[3:].strip(), []
        elif cur:
            buf.append(l)
    if cur:
        yield cur, "".join(buf)


FALLBACKS = ("vertex/gemini-3.8-flash", "vertex/gemini-3.7-flash")  # argon returns no text on about a quarter of the pages


def one(item):
    half, text = item
    err = ""
    for model in (MODEL,) + FALLBACKS:
        extra = ["-o", "max_output_tokens", os.environ["RENDER_MAX_TOKENS"]] if os.environ.get("RENDER_MAX_TOKENS") else []
        r = subprocess.run(["llm", "-n", "-m", model, "-o", "tier", "standard", *extra, PROMPT + text], capture_output=True,
                           text=True, timeout=900, stdin=subprocess.DEVNULL)
        m = re.search(r"\{.*\}", r.stdout, re.S)
        try:
            d = json.loads(m.group(0))
            return {"half": half, "model": model, "german": d["german"], "english": d["english"]}
        except Exception:
            err = (r.stdout + r.stderr)[-300:]
    return {"half": half, "error": err}


def main():
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["half"] for l in open(OUT) if '"error"' not in l}
    todo = [(h, t) for h, t in halves() if h not in done and "[" in t]
    print(len(todo), "halves to render", flush=True)
    with cf.ThreadPoolExecutor(8) as ex, open(OUT, "a") as o:
        for n, rec in enumerate(ex.map(one, todo), 1):
            o.write(json.dumps(rec, ensure_ascii=False) + "\n"); o.flush()
            if n % 25 == 0:
                print(n, "done", flush=True)


if __name__ == "__main__":
    main()
