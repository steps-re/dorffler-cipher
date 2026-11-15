"""Download a file only if its sha256 matches a pin from a checked-in file.

  python3 -I fetch_pinned.py fetch URL NAME OUT_DIR PINFILE HOST[,HOST...]
  python3 -I fetch_pinned.py verify FILE PINFILE

PINFILE lines are "<64 hex>  <name>" (sha256sum format). Compute each pin yourself from an
independent fetch (or the publisher's signed release notes). NEVER read the hash from the same
server that serves the file: whoever swaps the file swaps the hash.

Guarantees:
  - the output name comes from NAME (which must have exactly one pin), never from the URL or a header
  - https only, and the host must be in HOSTS, on the first request AND on every redirect hop
  - bytes are streamed to NAME.partial, hashed, and renamed to NAME only on a match
  - on any failure nothing is left behind and the exit status is 1
"""
import hashlib
import os
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_list  # noqa: E402

PIN_LINE = re.compile(r"([0-9a-f]{64})  (\S+)")
MAX_BYTES = 8 << 30


class FetchError(Exception):
    pass


def load_pins(pinfile):
    pins = {}
    for n, line in enumerate(open(pinfile, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = PIN_LINE.fullmatch(line)
        if not m or not safe_list.valid_name(m.group(2)):
            raise FetchError("%s:%d: malformed pin line" % (pinfile, n))
        if m.group(2) in pins:
            raise FetchError("%s:%d: duplicate pin for %s" % (pinfile, n, m.group(2)))
        pins[m.group(2)] = m.group(1)
    return pins


def check_url(url, hosts, schemes=("https",)):
    p = urllib.parse.urlparse(url)
    if p.scheme not in schemes or p.hostname not in hosts:
        raise FetchError("URL not allowlisted: %s://%s" % (p.scheme, p.hostname))


class CheckedRedirect(urllib.request.HTTPRedirectHandler):
    max_redirections = 5

    def __init__(self, hosts, schemes):
        self.hosts, self.schemes = hosts, schemes

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl, self.hosts, self.schemes)  # re-check EVERY hop
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, name, out_dir, pins, hosts, schemes=("https",), timeout=600, max_bytes=MAX_BYTES):
    """Return the final path. `schemes` exists so tests can use a local http server; the CLI never widens it."""
    hosts = frozenset(hosts)
    if name not in pins:
        raise FetchError("no pin for %r" % name)
    check_url(url, hosts, schemes)
    final = os.path.join(out_dir, name)
    part = final + ".partial"
    h, n = hashlib.sha256(), 0
    try:
        opener = urllib.request.build_opener(CheckedRedirect(hosts, schemes))
        with opener.open(url, timeout=timeout) as r:
            check_url(r.geturl(), hosts, schemes)
            with open(part, "wb") as f:
                for b in iter(lambda: r.read(1 << 20), b""):
                    n += len(b)
                    if n > max_bytes:
                        raise FetchError("download exceeds %d bytes" % max_bytes)
                    h.update(b)
                    f.write(b)
        if h.hexdigest() != pins[name]:
            raise FetchError("PIN MISMATCH for %s: got %s" % (name, h.hexdigest()))
        os.replace(part, final)
        return final
    finally:
        if os.path.exists(part):
            os.remove(part)


def verify(path, pins):
    name = os.path.basename(path)
    if name not in pins:
        raise FetchError("no pin for %r" % name)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    if h.hexdigest() != pins[name]:
        raise FetchError("PIN MISMATCH for %s" % name)


def main(argv):
    try:
        if len(argv) == 7 and argv[1] == "fetch":
            _, _, url, name, out_dir, pinfile, hosts = argv
            print(fetch(url, name, out_dir, load_pins(pinfile), hosts.split(",")))
        elif len(argv) == 4 and argv[1] == "verify":
            verify(argv[2], load_pins(argv[3]))
            print("ok")
        else:
            sys.exit(__doc__)
    except (FetchError, OSError) as e:
        print("fetch_pinned: %s" % e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
