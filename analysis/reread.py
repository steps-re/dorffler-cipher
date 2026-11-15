"""Read every cipher page-half: whole lines (clear German + numbers + interlinear decrypts).

Two independent readers. Resumes from data/reread.jsonl; a lock stops a second copy.

  python3 analysis/reread.py fetch    # full-resolution cipher pages from Riksarkivet IIIF, split into halves
  python3 analysis/reread.py read     # both readers -> data/reread.jsonl
Done-test: every (half, reader) pair has a record without "error".
The list of cipher pages is data/cipher_pages.txt (one "volume/pNNNN" per line, from a page triage).
"""
import fcntl, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as P

READERS = ["vertex/gemini-4-argon", "vertex/gemini-3.7-flash"]
OUT = os.path.join(P.D, "reread.jsonl")


def cipher_pages():
    return [l.strip() for l in open(os.path.join(P.D, "cipher_pages.txt")) if l.strip()]


def fetch():
    by_vol = {}
    for page in cipher_pages():
        v, p = page.split("/")
        by_vol.setdefault(v, []).append(int(p[1:]))
    for v, nums in sorted(by_vol.items()):
        full = os.path.join(P.D, "full", v)
        subprocess.run([sys.executable, "-I", os.path.join(P.REPO, "fetch_iiif.py"),
                        os.path.join(P.REPO, "manifests", v + ".json"), "riksarkivet", full, "lbiiif.riksarkivet.se"],
                       env=dict(os.environ, FETCH_ONLY=",".join(map(str, nums))), check=True)
        hd = os.path.join(P.D, "halves", v)
        os.makedirs(hd, exist_ok=True)
        for n in nums:
            P.halves(os.path.join(full, "p%04d.jpg" % n), hd, "p%04d" % n)
    print("halves ready:", 2 * len(cipher_pages()))


def read():
    lock = open(OUT + ".lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    prompt = open(os.path.join(P.A, "reread_prompt.txt")).read()
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            r = json.loads(l)
            if "error" not in r:
                done.add((r["half"], r["model"]))
    jobs = []
    for page in cipher_pages():
        v, p = page.split("/")
        for s in "LR":
            half = "%s/%s%s" % (v, p, s)
            for m in READERS:
                if (half, m) not in done:
                    jobs.append((half, m, os.path.join(P.D, "halves", v, p + s + ".jpg")))
    print(len(jobs), "reads to do", flush=True)

    def one(job):
        half, m, path = job
        text, err = P.ask(m, path, prompt, timeout=600, tier="standard")
        return {"half": half, "model": m, "text": text} if text else {"half": half, "model": m, "error": err}

    P.run_pool(jobs, one, OUT, workers=8)


if __name__ == "__main__":
    {"fetch": fetch, "read": read}[sys.argv[1]]()
