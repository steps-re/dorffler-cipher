# Simon Dörffler's cipher despatches

A transcription, a tested key and a full decode of the coded passages in the despatches of Simon Dörffler, Swedish resident at the Polish court, to King Charles XI, 1682-1690. Source: Riksarkivet SE/RA/2115/I/19/100, 101, 102 and 103 (Polonica), Public Domain Mark.

**Where it stands (24 Nov 2026):** The original 1680s key has been found at Riksarkivet (Chifferklaver vol. 3, folder III:20, "Clavis Positiva et Resolutiva mit Resident Dörfler") and transcribed to `data/key_original.json`. On the held-out test half it reproduces 75.8% of the clerk's decryption letters, against 73.9% for the key we inferred and 71.6% for TABLE-C04 unchanged (shuffled original key 14.0%, best of 200: 16.6%). Of the 21 values we inferred before the key was found, 17 match it, 3 differ only in spelling and 1 is wrong (`148`, we said `an`, the original says `ation`). A key-guided re-read of 2,500 suspect cipher numbers then changed 244 digits and moved the test half from 75.85% to 76.32% and the 813 fresh lines from 77.48% to 77.99%. The same number of random digit edits drops the test half to 75.0%. What is still missed is not the key and mostly not the digits. It is most likely clerk spelling and shorthand, and decryptions paired with the wrong coded line.

**Before the original key was found:** On a full-resolution strip reading of the pages, TABLE-C04 unchanged reproduces 71.6% of the clerk's decryption letters on the held-out test half (415 decryption lines, 14482 letters, odd pages outside 19/102). A shuffled key reproduces 10.5% (best of 200: 14.1%). On all 813 decryption lines outside 19/102 (28847 letters) from pages that Brice Dudout and Daniel Bourdeau never used, TABLE-C04 unchanged reproduces 73.0% (shuffled key 10.4%, best of 200: 13.7%). Adding 15 agreed fills and 6 proposals from the fit half brings the held-out test half to 73.9% (shuffled key 11.5%, best of 200: 15.8%) and the 813 fresh lines to 75.6% (shuffled key 11.4%, best of 200: 13.9%). The reading covers 270 half-pages and 26270 cipher numbers. Only 4.4% of cipher numbers lack a key value under TABLE-C04, and 3.3% under the final key.

The key is built on **TABLE-C04 by Brice Dudout**, published in Daniel Bourdeau's [cyphersolver](https://github.com/dbourdeau/cyphersolver/tree/main/research/dudout_dorffler1773). Dudout worked out the layout of the code and built the table. Mike German chose the data split and the measure, made the transcription and ran the test. This repository adds:
- a strip transcription of volumes 19/100, 19/101, 19/102 and 19/103 across 270 half-pages and 26270 cipher numbers
- a character-level test on the held-out test half and on 813 fresh decryption lines from pages the table's authors never used
- the finding that C04's word list (146-226) and names list (250+) are alphabetical (95% and 99% of pairs in order, with v-words sorting before u-words), while 227-249 is a non-alphabetical supplement (`ein`, `dreissig`, `tausend`, `zwey`, `drey`)
- 15 agreed fills and 6 weaker proposals, all found on the fit half only by two-set cloze agreement
- the mechanical decode of every coded page

## What is here

| Path | What it is |
|---|---|
| `results/overview.md` | What the coded passages are about, by volume, with page references (model-written from the page summaries, original key) |
| `results/reading.md` | Readable German of the coded half-pages with the original key on the re-read reading, with a one-line English summary |
| `analysis/reading.py`, `data/reading_original/` | Builds `reading.md` and `overview.md`, and the model readings they come from |
| `results/decoded.txt` | Mechanical decode: plain German, each cipher number replaced by its key value in [brackets], clerk's decryptions on `G:` lines |
| `results/key_final.json` | The final key: TABLE-C04 + 15 fills + 6 proposals |
| `results/key_changes.tsv` | Every change from TABLE-C04 and its fit-half evidence, plus the 28 additions of 15 Nov that were withdrawn and why |
| `results/evaluation.txt` | The test figures |
| `data/key_original.json` | The original 1680s key, transcribed by eye from the Riksarkivet scans (nulls 1-13, 155, 349 and up) |
| `results/original_key_report.txt` | Original key scored against TABLE-C04 and our final key, and every entry where they differ |
| `results/decoded_original_key.txt` | Mechanical decode of every coded page with the original key |
| `data/reread_keyguided/` | Key-guided re-read: suspects, model answers, accepted changes and the re-read reading `p5_lines.jsonl` |
| `results/numfix_report.txt` | Re-read scores, the random-edit control and sample changes |
| `analysis/original_key.py` | Scores the original key (`decode` writes the full decode) |
| `analysis/numfix.py` | Key-guided re-read: detect, locate, ask, apply, score |
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

### The original key

The key was ordered from Riksarkivet (copy order RA-FF 2026/100525, 24 Nov 2026) after the inferred key was published. Its 2 pages were transcribed by eye from 300 dpi scans. No part of it was fitted to the clerk's decryptions, so every line is held out.

| Subset | Lines / letters | TABLE-C04 | C04 + 15 fills + 6 proposals | Original key | Shuffled original key |
|---|---|---|---|---|---|
| Held-out test half | 415 lines, 14482 letters | 71.6% | 73.9% | 75.8% | 14.0% (best of 200: 16.6%) |
| Fresh lines | 813 lines, 28847 letters | 73.0% | 75.6% | 77.5% | 14.3% (best of 200: 16.9%) |
| Fit half | 954 lines, 31534 letters | 60.3% | 62.5% | 63.8% | 13.1% (best of 200: 15.5%) |
| All lines | 1369 lines, 46016 letters | 63.9% | 66.1% | 67.6% | 13.4% (best of 200: 15.7%) |

These figures are on the strip reading in `data/p5_lines.jsonl`. The original key gives a value to every cipher number. 2.8% of the numbers in the reading are nulls it declares meaningless. TABLE-C04 matches 179 of its 333 entries and our final key 196. Most of the rest are entries C04 left empty, or short forms of the same word (`des` for `dess`, `sol` for `soll`). 12 C04 values are a different word: `100 lich` (original `ku`), `170 ihr` (`gegen`), `171 ca` (`genug`), `176 wah` (`heut`), `180 lich` (`ition`), `210 wider` (`viel`), `224 wolle` (`will`), `225 wir` (`wie`), `226 wer` (`wür`), `237 dreissig?` (`sechs`), `246 tausend?` (`zig`), `290 feld` (`elbe`). C04 also gives `10` the value `e`, where the original makes it a null.

Our 21 inferred values against the original: 17 right (`175 heit`, `191 mich`, `201 ohn`, `210 viel`, `213 uber`, `226 wur`, `230 zwischen`, `233 zwey`, `234 drey`, `253 alliance`, `269 churfurst`, `275 conjun`, `301 franckreich`, `307 general`, `312 hertzog`, `317 konig`, `336 schwed`), 3 spelling only (`254 ambassade` for `ambassad`, `295 ekm` for `ekmt`, `323 moscau` for `moscow`), 1 wrong (`148 an` for `ation`). Both of the values where we overruled C04 (`210 viel`, `226 wur`) are right.

### Key-guided re-read

`analysis/numfix.py` looked for cipher numbers that were probably misread. It used no clerk decryptions to find them. Each number was swapped for digits that look alike (8/0, 3/8, 1/7, 5/6, 4/9, 2/7, 3/5) and the decode of the 4 numbers either side was scored under a 17th-century German letter model. The top 2,500 suspects were cut from the full-resolution strip and shown to Gemini 4 Argon twice, blind to the key and to the decryptions, with the option order swapped. A number was changed only when both answers agreed (4,846 calls on research-agent-vm). 2,417 suspects were located on a strip, 1,990 got matching answers and 244 numbers were changed.

| Subset | Lines / letters | Before | After | Random-edit control |
|---|---|---|---|---|
| Held-out test half | 415 lines, 14482 letters | 75.85% | 76.32% | 74.99% (30 draws, max 75.26%) |
| Fresh lines | 813 lines, 28847 letters | 77.48% | 77.99% | 76.60% (max 76.73%) |
| Fit half | 828 lines, 30965 letters | 70.27% | 70.74% | 69.48% (max 69.65%) |

These figures use the original key unchanged, on the newest reading from cyphersolver (`research/dudout_dorffler1773/german2026/transcription/p5_lines.jsonl`). It differs from `data/p5_lines.jsonl` only on 19/102, which is why the fit half has 828 lines here. The re-read version is `data/reread_keyguided/p5_lines.jsonl`. Applying the top 244 language-model suspects with no image check gives a lower test half (75.64%) than doing nothing, so the image check is what carries the gain. A gain of half a point means the digits are no longer the main source of error.

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
python3 analysis/reading.py prep
CIPHER_DATA=data/reading_original python3 analysis/render.py
python3 analysis/reading.py md
python3 analysis/reading.py overview
python3 analysis/original_key.py
python3 analysis/original_key.py decode
python3 analysis/numfix.py detect   # then locate, ask (on a VM), apply, score
```

Model readings differ slightly from run to run. The published files in `data/` are the ones the figures come from.

## Known gaps

- Of the 26270 cipher numbers in the reading, 4.4% have no key value in TABLE-C04 and 3.3% have no key value in `results/key_final.json`.
- 15 numbers tested in the cloze run did not agree across the 2 sets and stayed unknown in our final key: `160`, `161`, `168`, `172`, `182`, `186`, `187`, `189`, `198`, `200`, `202`, `217`, `229`, `239`, `300`. The original key gives all of them (`160 doch`, `200 offt`, `300 flotte` and so on).
- The numbers under 14 in the earlier reading were misreads (07 for 87, 02 for 82). They carry no key value.
- Volume 19/102 scores lower than the other volumes (47.7% with C04 unchanged, 48.9% with the final key) because the clerk ink is pale.
- The original key was transcribed by one reader from scans. In the Kurrent hand `e` looks like `r` (156 `der`, 222 `wer`), and one entry (`344`) is marked `?` in `data/key_original.json`.
- `results/reading.md` has no readable version of 19/102 image 475, right half, because no model returned one. Its decode is in `results/decoded_original_key.txt`.
- No person has read the decode against the page images.

## Licence and citation

Code is MIT (`LICENSE`). Data and results are CC BY 4.0 (`LICENSE-DATA.md`). Credit goes to Brice Dudout and Daniel Bourdeau for TABLE-C04 in `cyphersolver` (`research/dudout_dorffler1773/`), and to Mike German for the transcription, split, measure and test.
