# Data licence

Everything under `data/` and `results/` is licensed **CC BY 4.0** (https://creativecommons.org/licenses/by/4.0/),
except where noted below. Code (`*.py`) is MIT, see `LICENSE`.

- `data/key_c04.json` and `data/bourdeau/` are TABLE-C04 and its notes by Brice Dudout (Europe chiffrée),
  published in github.com/dbourdeau/cyphersolver, `research/dudout_dorffler1773/`, CC BY 4.0. Copied unchanged.
- `results/key_final.json` is a derivative of TABLE-C04 (changes listed in `results/key_changes.tsv`).
- The manuscripts are Riksarkivet SE/RA/2115/I/19/100-103, Public Domain Mark. No images are included;
  `manifests/` points to the archive's IIIF service.
- The language model (`analysis/lm.py`) is built from the Deutsches Textarchiv (CC BY-SA 4.0). The corpus
  and the built model are not included; `lm.py build` recreates them.

Please cite as: Steps Ventures (2026), "Simon Dörffler's cipher despatches 1682-1690: transcription, key and
decode", github.com/steps-re/dorffler-cipher, building on B. Dudout, TABLE-C04.
