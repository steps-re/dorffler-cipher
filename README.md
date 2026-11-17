# Simon Dörffler's cipher despatches

A transcription, a tested key and a full decode of the coded passages in the despatches of Simon Dörffler, Swedish resident at the Polish court, to King Charles XI, 1682-1690. Source: Riksarkivet SE/RA/2115/I/19/100, 101, 102 and 103 (Polonica), Public Domain Mark.

**Where it stands:** On a full-resolution strip reading of the pages, TABLE-C04 unchanged reproduces 71.6% of the clerk's decryption letters on the held-out test half (415 decryption lines, 14482 letters, odd pages outside 19/102). A shuffled key reproduces 10.5% (best of 200: 14.1%). On all 813 decryption lines outside 19/102 (28847 letters) from pages that Brice Dudout and Daniel Bourdeau never used, TABLE-C04 unchanged reproduces 73.0% (shuffled key 10.4%, best of 200: 13.7%). Adding 15 agreed fills and 6 proposals from the fit half brings the held-out test half to 73.9% (shuffled key 11.5%, best of 200: 15.8%) and the 813 fresh lines to 75.6% (shuffled key 11.4%, best of 200: 13.9%). The reading covers 270 half-pages and 26270 cipher numbers. Only 4.4% of cipher numbers lack a key value under TABLE-C04, and 3.3% under the final key.

The key is built on **TABLE-C04 by Brice Dudout**, published in Daniel Bourdeau's [cyphersolver](https://github.com/dbourdeau/cyphersolver/tree/main/research/dudout_dorffler1773). Dudout worked out the layout of the code and built the table. Mike German chose the data split and the measure, made the transcription and ran the test. This repository adds:
- a strip transcription of volumes 19/100, 19/101, 19/102 and 19/103 across 270 half-pages and 26270 cipher numbers
- a character-level test on the held-out test half and on 813 fresh decryption lines from pages the table's authors never used
- the finding that C04's word list (146-226) and names list (250+) are alphabetical (95% and 99% of pairs in order, with v-words sorting before u-words), while 227-249 is a non-alphabetical supplement (`ein`, `dreissig`, `tausend`, `zwey`, `drey`)
- 15 agreed fills and 6 weaker proposals, all found on the fit half only by two-set cloze agreement
- the mechanical decode of every coded page

## What is here

| Path | What it is |
|---|---|
| `results/overview.md` | What the coded passages are about, by volume, with page references (model-written from the page summaries) |
| `results/reading.md` | Readable German of the coded half-pages, with a one-line English summary |
| `results/decoded.txt` | Mechanical decode: plain German, each cipher number replaced by its key value in [brackets], clerk's decryptions on `G:` lines |
| `results/key_final.json` | The final key: TABLE-C04 + 15 fills + 6 proposals |
| `results/key_changes.tsv` | Every change from TABLE-C04 and its fit-half evidence, plus the 28 additions of 15 Nov that were withdrawn and why |
| `results/evaluation.txt` | The test figures |
| `data/reread.jsonl` | Whole-page readings: two model reads per half-page |
| `data/strips_full.jsonl` | Full-resolution strip readings: 5 overlapping strips per half-page (25% of page height, 6% overlap) read by Gemini 4 Argon |
| `data/strips_retry.jsonl` | Finer strip readings (15% of page height) for pages re-read at smaller strip height |
| `data/p5_lines.jsonl` | The new merged reading across 270 half-pages (249 from 25%-height strips, 8 from 15%-height strips, 13 kept from the whole-page reading) |
| `data/cloze.jsonl` | Split-half cloze proposals and validation runs on the fit half |
| `data/p5_lines.whole_page.jsonl` | The earlier whole-page reading, kept for comparison |
| `data/key_c04.json`, `data/bourdeau/` | TABLE-C04 and its notes, unchanged, CC BY 4.0, B. Dudout |
| `analysis/strips.py` | Cuts each half-page into overlapping full-resolution strips and reads them with Gemini 4 Argon without the key |
| `analysis/consensus.py` | Stitches the strip reads, applies the key-free sanity check, and writes `data/p5_lines.jsonl` |
| `analysis/align.py` | Whole-page alignment of clerk decryption lines to cipher lines |
| `analysis/cloze.py` | Two-set fit-half cloze key filling and validation on hidden C04 entries |
| `analysis/` | Supporting scripts for fetching, scoring, decoding and rendering (Python 3) |

## Results

| Subset | Lines / letters | Key | Score | Shuffled key |
|---|---|---|---|---|
| Held-out test half (odd pages outside 19/102) | 415 lines, 14482 letters | TABLE-C04 unchanged | 71.6% | 10.5% (best of 200: 14.1%) |
| Held-out test half (odd pages outside 19/102) | 415 lines, 14482 letters | C04 + 15 fills + 6 proposals | 73.9% | 11.5% (best of 200: 15.8%) |
| Fresh lines (outside 19/102, pages Dudout/Bourdeau never used) | 813 lines, 28847 letters | TABLE-C04 unchanged | 73.0% | 10.4% (best of 200: 13.7%) |
| Fresh lines (outside 19/102, pages Dudout/Bourdeau never used) | 813 lines, 28847 letters | C04 + 15 fills + 6 proposals | 75.6% | 11.4% (best of 200: 13.9%) |
| Fit half | 954 lines, 31534 letters | TABLE-C04 unchanged | 60.3% | 9.7% (best of 200: 12.7%) |
| Fit half | 954 lines, 31534 letters | C04 + 15 fills + 6 proposals | 62.5% | 10.3% (best of 200: 12.9%) |
| Volume 19/100 | 596 lines, 20730 letters | TABLE-C04 unchanged | 71.7% | 10.3% (best of 200: 12.9%) |
| Volume 19/100 | 596 lines, 20730 letters | C04 + 15 fills + 6 proposals | 75.1% | 11.1% (best of 200: 14.7%) |
| Volume 19/101 | 186 lines, 6444 letters | TABLE-C04 unchanged | 75.3% | 10.8% (best of 200: 13.3%) |
| Volume 19/101 | 186 lines, 6444 letters | C04 + 15 fills + 6 proposals | 77.1% | 11.4% (best of 200: 14.3%) |
| Volume 19/102 | 510 lines, 15965 letters | TABLE-C04 unchanged | 47.7% | 9.0% (best of 200: 11.9%) |
| Volume 19/102 | 510 lines, 15965 letters | C04 + 15 fills + 6 proposals | 48.9% | 9.5% (best of 200: 12.2%) |
| Volume 19/103 | 77 lines, 2877 letters | TABLE-C04 unchanged | 71.4% | 11.1% (best of 200: 15.9%) |
| Volume 19/103 | 77 lines, 2877 letters | C04 + 15 fills + 6 proposals | 71.6% | 11.8% (best of 200: 15.7%) |

### Strip reading

Every half-page was cut into 5 overlapping full-resolution strips (25% of page height, 6% overlap), read by Gemini 4 Argon, and stitched (1,360 calls, 5 failures). The key was never shown to the reader. In a pilot on 3 pages, 5 strips did as well as 11. Of the 270 half-pages, 249 come from 25%-height strips, 8 come from 15%-height strips, and 13 are kept from the earlier whole-page reading because the strip read failed a key-free sanity check. A second pass at 11 strips on all of 19/102 plus a 3-reader majority vote changed 134 numbers and moved the fit half from 60.1% to 60.3%. This showed no real gain and confirmed that the reader is at its plateau.

Whole-page reads misread single digits systematically, especially 8 as 0 (28 read as 20, 18 as 10, 87 as 07). An independent blind read of 2 pages by a different model family (Claude) agreed with the strip read on 93.7% and 85.7% of numbers, against 91.0% and 80.2% for the whole-page reading.

Whole-page alignment of clerk lines to cipher (`analysis/align.py`) gave no gain over next-two-lines pairing (60.9% vs 62.1% on the whole-page reading's test half, with a 0.3% shuffled control). Line pairing was not the bottleneck.

### Key fills and proposals

In `analysis/cloze.py`, the fit-half occurrences of each target number are dealt into 2 disjoint sets. Gemini 4 Argon proposes a value from each set separately. A fill is kept only if both sets agree. To validate the method, 62 known C04 entries were hidden. Both sets agreed on 58, and 53 of the 58 matched C04 (91%). Of the 5 misses, 3 are a longer form of the same word (`ihr`/`ih`, `wie`/`wi`, `preussen`/`preussi`) and 2 disagree with C04: `210 viel` (C04 `wider`) and `226 wur` (C04 `wer`). C04's value for 210 is never reproduced by the clerk on the fit half.

- **15 agreed fills:** `148 an`, `175 heit`, `191 mich`, `201 ohn`, `213 uber`, `230 zwischen`, `233 zwey`, `234 drey`, `253 alliance`, `254 ambassade`, `269 churfurst`, `275 conjun`, `307 general`, `323 moscau`, `336 schwed`.
- **6 weaker proposals (marked as such):** `210 viel`, `226 wur`, `317 konig` (C04 `KOENIG`, clerk spells `König`), `301 franckreich` (C04 `FRANKREICH`), `312 hertzog` (the 2 sets gave `herzog`/`hertzog`), `295 ekm` (both sets read it as the address `Euer Königliche Majestät`).

An earlier version of this repository reported 64.7% for 28 additions of 15 Nov. That figure was withdrawn because of a test-half leak found by Daniel Bourdeau. All evidence for the current fills comes from the fit half only.

## Reproduce

```
python3 analysis/reread.py fetch
python3 analysis/reread.py read
python3 analysis/strips.py read $(cat data/strip_halves.txt) --model vertex/gemini-4-argon --height 0.25 --overlap 0.06 --out data/strips_full.jsonl
python3 analysis/consensus.py
python3 analysis/cloze.py run
python3 analysis/cloze.py report
python3 analysis/p5.py score data/key_c04.json
python3 analysis/p5.py score results/key_final.json
python3 analysis/p5.py decode results/key_final.json
python3 analysis/render.py
```

Model readings differ slightly from run to run. The published files in `data/` are the ones the figures come from.

## Known gaps

- Of the 26270 cipher numbers in the reading, 4.4% have no key value in TABLE-C04 and 3.3% have no key value in `results/key_final.json`.
- 15 numbers tested in the cloze run did not agree across the 2 sets and stay unknown: `160`, `161`, `168`, `172`, `182`, `186`, `187`, `189`, `198`, `200`, `202`, `217`, `229`, `239`, `300`.
- `results/reading.md` and `results/overview.md` were made from the earlier whole-page reading and key. They have not been redone on the strip reading.
- The numbers under 14 in the earlier reading were misreads (07 for 87, 02 for 82). They carry no key value.
- Volume 19/102 scores lower than the other volumes (47.7% with C04 unchanged, 48.9% with the final key) because the clerk ink is pale.
- The original codebook has not been found online. DECODE has no Dörffler record. Riksarkivet Chifferklaver (SE/RA/202, volumes 3 and 7, card index volumes 20-21) is on paper only.
- No person has read the decode against the page images.

## Licence and citation

Code is MIT (`LICENSE`). Data and results are CC BY 4.0 (`LICENSE-DATA.md`). Credit goes to Brice Dudout and Daniel Bourdeau for TABLE-C04 in `cyphersolver` (`research/dudout_dorffler1773/`), and to Mike German for the transcription, split, measure and test.
