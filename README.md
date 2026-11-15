# Simon Dörffler's cipher despatches, 1682-1690

A transcription, a tested key and a full decode of the coded passages in the despatches of Simon Dörffler, Swedish resident at the Polish court, to King Charles XI. Source: Riksarkivet SE/RA/2115/I/19/100, 101, 102 and 103 (Polonica), Public Domain Mark.

**Where it stands:** the key works on all four volumes. On held-out pages it reproduces 65% of the letters that a clerk in the 1680s wrote over the cipher. A shuffled key reproduces 12%. 97.4% of the 26,070 cipher numbers have a key value. Every coded page has a mechanical decode, and 243 of 250 half-pages also have a readable version. `METHOD.md` explains how, in plain terms.

The key is built on **TABLE-C04 by Brice Dudout** (Europe chiffrée), published in Dan Bourdeau's [cyphersolver](https://github.com/dbourdeau/cyphersolver/tree/main/research/dudout_dorffler1773) (CC BY 4.0). Dudout worked out the layout of the code. This repository adds:
- a transcription of all four volumes
- a character-level test on pages the table's authors never used
- 28 new or changed entries
- the decode

## What is here

| Path | What it is |
|---|---|
| `results/overview.md` | What the coded passages are about, by volume, with page references (model-written from the page summaries) |
| `results/reading.md` | Readable German of every coded half-page, with a one-line English summary (model-made, see METHOD Step 5) |
| `results/decoded.txt` | Mechanical decode: plain German, each cipher number replaced by its key value in [brackets], clerk's decryptions on `G:` lines |
| `results/key_final.json` | The key: number to letters. Upper-case values are names or titles kept from TABLE-C04 |
| `results/key_changes.tsv` | Every change from TABLE-C04 and the evidence for it (clerk's votes, or a model proposal kept because it raised the fit-half score) |
| `results/evaluation.txt` | The test figures |
| `data/reread.jsonl` | Raw readings: two models per half-page |
| `data/p5_lines.jsonl` | Merged lines after the image check (`settled` says how each disputed number was decided). The pre-check version is `p5_lines.before_adjudication.jsonl` |
| `data/key_c04.json`, `data/bourdeau/` | TABLE-C04 and its notes, unchanged, CC BY 4.0, B. Dudout |
| `analysis/` | The code (Python 3, standard library plus Pillow; model calls via the `llm` CLI) |

## Results

| Key | Held-out half (422 decryption lines, 14,245 letters) | Shuffled key |
|---|---|---|
| TABLE-C04 as published | 62.1% | 10.3% (best of 200: 13.8%) |
| `results/key_final.json` | **64.7%** | 11.9% (best of 200: 14.6%) |

On all 825 decryption lines outside 19/102 that Dudout and Bourdeau never used, TABLE-C04 scores 66.0%.

Scores are a floor. The clerk's decryptions are paraphrases in places, some are attached to the wrong line, and single digits are misread. So even a perfect key would score well under 100%.

A tempting shortcut fails, and is kept as a documented negative result. Tuning the key so the decode "reads like German" under a model of 1,114 German texts from 1600-1699 made it worse on the test (`analysis/refine.py`).

## Reproduce

```
python3 analysis/reread.py fetch     # cipher pages from Riksarkivet IIIF, at reading pace (about 8 h)
python3 analysis/reread.py read      # two model readings per half-page
python3 analysis/p5.py merge
python3 analysis/p5.py score data/key_c04.json
python3 analysis/p5.py vote          # clerk votes, fit/test split
python3 analysis/p5.py fill          # model-proposed values for missing numbers, kept only if the fit half improves
python3 analysis/adjudicate.py look  # re-check each number the two readers disagree on against the image
python3 analysis/adjudicate.py apply
python3 analysis/p5.py decode data/key_final.json
python3 analysis/render.py           # readable version
```
Model readings will differ from run to run. The published `data/` files are the ones the figures come from.

## Known gaps

- About 2.6% of the numbers have no value.
- Values marked medium in `key_changes.tsv` are the least certain. So is 230, read as "alliance zwischen", which may be two codes.
- Seven half-pages have no readable version, because all three models returned no text.
- No one has yet read the whole decode against the images by eye.

## Licence and citation

Code MIT (`LICENSE`), data and results CC BY 4.0 (`LICENSE-DATA.md`).
Cite as: Steps Ventures (2026), *Simon Dörffler's cipher despatches 1682-1690: transcription, key and decode*, github.com/steps-re/dorffler-cipher, building on B. Dudout, TABLE-C04, in D. Bourdeau, cyphersolver.
