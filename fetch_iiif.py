"""Fetch every page image of one IIIF manifest, slowly, like a reader would.

  python3 -I fetch_iiif.py MANIFEST.json KIND OUT_DIR HOST[,HOST...]

KIND is "riksarkivet" (IIIF v3, full/max), "riksarkivet1600" (1600 px wide) or "vatlib" (IIIF v2, full/full).
FETCH_ONLY=3,17,240 limits the run to those canvas numbers (e.g. full-resolution cipher pages).
Output names come from the canvas index (p0001.jpg ...), never from the URL or a header.
Pacing: 8-25 s between requests, a 60-180 s pause every 40-70 pages. Pages already on disk
are skipped, so a restart resumes. A 5xx gets one retry after a 2-5 min wait. Anything else
(403, 429, a block page, a second failure) stops the run (exit 2).
"""
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_pinned import CheckedRedirect, check_url  # noqa: E402

UA = "Mozilla/5.0 (research)"  # no personal address in requests to third parties
MAX_BYTES = 40 << 20


def urls(manifest, kind):
    m = json.load(open(manifest, encoding="utf-8"))
    if kind in ("riksarkivet", "riksarkivet1600"):
        for c in m["items"]:
            u = c["items"][0]["items"][0]["body"]["id"]            # .../full/max/0/default.jpg
            # 1600 px wide is what triage reads; same request count, a fraction of the bytes
            # "!1600,1600" = fit inside 1600x1600. "1600," asked the server to ENLARGE narrow pages
            # (19/101 p2 is 936 px wide) and IIIF level 1 refuses that with HTTP 400.
            yield u.replace("/full/max/", "/full/!1600,1600/") if kind == "riksarkivet1600" else u
    elif kind == "vatlib":
        for c in m["sequences"][0]["canvases"]:
            svc = c["images"][0]["resource"]["service"]["@id"]
            yield svc + "/full/full/0/native.jpg"
    else:
        sys.exit("unknown KIND")


def get(url, hosts):
    check_url(url, hosts)
    op = urllib.request.build_opener(CheckedRedirect(hosts, ("https",)))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with op.open(req, timeout=120) as r:
        if r.status != 200 or not r.headers.get("Content-Type", "").startswith("image/"):
            raise RuntimeError("not an image: %s %s" % (r.status, r.headers.get("Content-Type")))
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or data[:3] != b"\xff\xd8\xff":
        raise RuntimeError("bad jpeg (%d bytes)" % len(data))
    return data


def main(manifest, kind, out, hosts):
    hosts = set(hosts.split(","))
    os.makedirs(out, exist_ok=True)
    only = {int(x) for x in os.environ.get("FETCH_ONLY", "").split(",") if x.strip().isdigit()}
    todo = [(i, u) for i, u in enumerate(urls(manifest, kind), 1)
            if not os.path.exists(os.path.join(out, "p%04d.jpg" % i)) and (not only or i in only)]
    print("%d pages to fetch" % len(todo), flush=True)
    next_pause = random.randint(40, 70)
    for n, (i, u) in enumerate(todo, 1):
        try:
            try:
                data = get(u, hosts)
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    raise
                print("p%04d: HTTP %d, one retry after a pause" % (i, e.code), flush=True)
                time.sleep(random.uniform(120, 300))
                data = get(u, hosts)
        except Exception as e:  # stop at a refusal or a second failure, never retry in a loop
            print("STOP p%04d: %s" % (i, e), flush=True)
            return 2
        path = os.path.join(out, "p%04d.jpg" % i)
        with open(path + ".partial", "wb") as f:
            f.write(data)
        os.replace(path + ".partial", path)
        print("p%04d %d" % (i, len(data)), flush=True)
        time.sleep(random.uniform(8, 25))
        if n == next_pause:
            time.sleep(random.uniform(60, 180))
            next_pause += random.randint(40, 70)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
