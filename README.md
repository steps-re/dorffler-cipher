# Simon Dörffler's cipher despatches, 1682-1690

A transcription, a tested key and a full decode of the coded passages in the despatches of Simon Dörffler, Swedish resident at the Polish court, to King Charles XI. Source: Riksarkivet SE/RA/2115/I/19/100, 101, 102 and 103 (Polonica), Public Domain Mark.

**Where it stands:** TABLE-C04 works on all four volumes. On 825 decryption lines from pages its authors never used, it reproduces 66% of the letters that a clerk in the 1680s wrote over the cipher. A shuffled key reproduces 10%. No change we tested improves on C04 by more than chance. About 96% of the cipher numbers have a key value. Every coded page has a mechanical decode, and 243 of 250 half-pages also have a readable version. `METHOD.md` explains how, in plain terms.

The key is built on **TABLE-C04 by Brice Dudout** (Europe chiffrée), published in Dan Bourdeau's [cyphersolver](https://github.com/dbourdeau/cyphersolver/tree/main/research/dudout_dorffler1773) (CC BY 4.0). Dudout worked out the layout of the code. This repository adds:
- a transcription of all four volumes
- a character-level test on pages the table's authors never used
- the finding that C04's word list (146-249) and names list (250 and up) are in alphabetical order, which bounds every missing value
- 17 new or changed entries, all chosen on the fit half only (see Results: none is a measurable gain)
- the decode

## What is here

| Path | What it is |
|---|---|
| `results/overview.md` | What the coded passages are about, by volume, with page references (model-written from the page summaries) |
| `results/reading.md` | Readable German of every coded half-page, with a one-line English summary (model-made, see METHOD Step 5) |
| `results/decoded.txt` | Mechanical decode: plain German, each cipher number replaced by its key value in [brackets], clerk's decryptions on `G:` lines |
| `results/key_final.json` | The key: number to letters. Upper-case values are names or titles kept from TABLE-C04 |
| `results/key_changes.tsv` | Every change from TABLE-C04 and its fit-half evidence, plus the 28 earlier additions that were withdrawn and why |
| `results/evaluation.txt` | The test figures |
| `data/reread.jsonl` | Raw readings: two models per half-page |
| `data/p5_lines.jsonl` | Merged lines after the image check (`settled` says how each disputed number was decided). The pre-check version is `p5_lines.before_adjudication.jsonl` |
| `data/key_c04.json`, `data/bourdeau/` | TABLE-C04 and its notes, unchanged, CC BY 4.0, B. Dudout |
| `analysis/` | The code (Python 3, standard library plus Pillow; model calls via the `llm` CLI) |

## Results

| Key | Held-out half (422 decryption lines, 14,245 letters) | Shuffled key |
|---|---|---|
| TABLE-C04 as published | 62.1% | 10.3% (best of 200: 13.8%) |
| C04 + 1 fit-half vote | 62.1% | 10.5% (best of 200: 13.5%) |
| + 14 alphabetical-order fills | 62.8% | 11.1% (best of 200: 14.0%) |
| `results/key_final.json` (+ 2 spelling fixes) | 62.9% | 11.3% (best of 200: 14.7%) |

On all 825 decryption lines outside 19/102 that Dudout and Bourdeau never used, TABLE-C04 scores 66.0%.

Every change was chosen on the fit half, and the test half was scored once at the end. The raw score rises 0.8 points, but the shuffled score rises 1.0, so the changes are not a measurable gain over C04. Against these decryptions C04 is at its ceiling. The missing third comes from reading and line pairing, not from the key.

An earlier version of this repository reported 64.7% for 28 additions. That figure was not held out: the clerk's votes were taken from every line, and the model that proposed values was shown test-half examples. Daniel Bourdeau found this. Those additions are withdrawn, and `results/key_changes.tsv` lists each one's fate.

Scores are a floor. The clerk's decryptions are paraphrases in places, some are attached to the wrong line, and single digits are misread. So even a perfect key would score well under 100%.

A tempting shortcut fails, and is kept as a documented negative result. Tuning the key so the decode "reads like German" under a model of 1,114 German texts from 1600-1699 made it worse on the test (`analysis/refine.py`).

## Reproduce

```
python3 analysis/reread.py fetch     # cipher pages from Riksarkivet IIIF, at reading pace (about 8 h)
python3 analysis/reread.py read      # two model readings per half-page
python3 analysis/p5.py merge
python3 analysis/p5.py score data/key_c04.json
python3 analysis/adjudicate.py look  # re-check each number the two readers disagree on against the image
python3 analysis/adjudicate.py apply
python3 analysis/p5.py vote          # clerk votes on the fit half -> data/key_fitvote.json
python3 analysis/order.py fill data/key_fitvote.json     # alphabetical-order fills -> data/key_order.json
python3 analysis/reassign.py data/key_order.json         # re-test entries never reproduced -> data/key_reassign.json
python3 analysis/p5.py decode data/key_reassign.json
python3 analysis/render.py           # readable version
```
Model readings will differ from run to run. The published `data/` files are the ones the figures come from.

## Known gaps

- About 4% of the numbers have no value.
- Fills supported by 2-5 fit-half places (241, 266, 275, 307, 315, 318, 328) are the least certain.
- `results/reading.md` and `results/overview.md` were made with the withdrawn key. They differ from a decode under the current key at the withdrawn values only (see `key_changes.tsv`).
- Seven half-pages have no readable version, because all three models returned no text.
- No one has yet read the whole decode against the images by eye.

## Licence and citation

Code MIT (`LICENSE`), data and results CC BY 4.0 (`LICENSE-DATA.md`).
Cite as: Steps Ventures (2026), *Simon Dörffler's cipher despatches 1682-1690: transcription, key and decode*, github.com/steps-re/dorffler-cipher, building on B. Dudout, TABLE-C04, in D. Bourdeau, cyphersolver.
