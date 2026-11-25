# How the Dörffler code was read

Written for a reader with a college education and no background in codebreaking. Every number here was measured on the data in this repository.

## The material

Simon Dörffler was Sweden's resident diplomat at the Polish court in the 1680s. His despatches to King Charles XI are ordinary German letters. The sensitive parts switch into numbers, for example `218. 77. 53. 66. 25.`. Four volumes of these despatches are digitized by the Swedish National Archives (Riksarkivet, SE/RA/2115/I/19/100-103, about 2,170 page images, Public Domain Mark). 136 of those pages carry code: about 26,000 numbers.

On many pages a clerk in Stockholm wrote the meaning of the numbers between the lines, in small pale German. We found about 1,400 such decrypted lines. They are the answer key a historian would want, but they are incomplete, not word for word, and often hard to read. So they can test a codebook, but they do not replace one.

## The code

The code is a syllabary with a word list, the usual design for the period (historians call it a nomenclator). Brice Dudout (Europe chiffrée) worked out its layout and published a first table, TABLE-C04, in Dan Bourdeau's cyphersolver repository on 14 November 2026:

- 14-39 and 40-65: two alphabets, so each letter has two numbers
- 66-145: syllables, 16 consonants times 5 vowels (ba, be, bi, bo, bu, ...)
- 146-231: common words (der, die, und, von, nicht, ...)
- 250 and up: names and titles (König, Pohlen, Bischof, ...)

Dudout tested the table on three held-out pages and called all three tests failed, because they fell short of thresholds he set in advance. This repository tests the same table on much more material, and it holds up.

## Step 1. Read every coded page, three times

**Two whole-page reads.** Two AI models, Google's Gemini 4 Argon and Gemini 3.7 Flash, each read every coded half-page in one pass. Each read kept everything: the plain German, the numbers in place, and the clerk's decryption on its own tagged line above the numbers it explains. Where the two disagreed on a number, Argon looked at the page again and picked one. The key was not used.

**Why that was not enough.** At whole-page scale the digits are small, and both models misread them the same way: 8 as 0. So 28 became 20, 18 became 10, and 87 became 07. A different model family (Claude) read two pages blind from full-size strips. It disagreed with the whole-page reading on 9.0% of the numbers on one page and 19.8% on the other.

**The strip read.** Every half-page was cut into 5 overlapping strips at full resolution (25% of the page height, 6% overlap). Gemini 4 Argon read each strip without ever seeing the key, and the strips were stitched back into lines. That took 1,360 model calls with 5 failures. In a 3-page pilot, 5 strips did as well as 11. The strip read agrees with the blind Claude read on 93.7% and 85.7% of the numbers on those two pages, against 91.0% and 80.2% for the whole-page reading.

**The final reading.** A strip read is used when it passes a check that does not involve the key: its count of numbers and of decryption letters must be close to the whole-page read's. Of 270 half-pages, 249 use the 5-strip read, 8 use an 11-strip read, and 13 keep the whole-page read. The reading has 26,270 cipher numbers.

## Step 2. A fair test

A key is good if decoding the numbers under a clerk's decryption gives back the clerk's letters. The score is the share of decryption letters that the decoding reproduces in order, counting only runs of three or more letters, because scattered single letters match by chance.

Chance is measured too. The same key with its entries shuffled among its numbers is scored 100-200 times. That shuffled score is what a meaningless key gets.

The pages were split before any key was changed:

- **Fit half:** volume 19/102, where the table was built, plus even-numbered pages of the other volumes.
- **Test half:** odd-numbered pages outside 19/102, 415 decryption lines and 14,482 letters in the final reading. These are never used to change the key.

## Step 3. Results

Share of the clerk's letters reproduced on the test half, with the same key shuffled as the control:

| Reading | Key | Test half | Shuffled key |
|---|---|---|---|
| Whole-page | TABLE-C04 as published | 62.1% | 10.3% (best of 200: 13.8%) |
| Strips | TABLE-C04 as published | 71.6% | 10.5% (best of 200: 14.1%) |
| Strips | C04 + 15 fills + 6 proposals | 73.9% | 11.5% (best of 200: 15.8%) |

The table did not change between the first two rows. Only the reading did. On the 813 decryption lines outside 19/102 from pages the table's authors never used, TABLE-C04 scores 73.0% and the final key 75.6%.

| Volume | TABLE-C04 | Final key |
|---|---|---|
| 19/100 | 71.7% | 75.1% |
| 19/101 | 75.3% | 77.1% |
| 19/102 | 47.7% | 48.9% |
| 19/103 | 71.4% | 71.6% |

So the key is real, and it works across all four volumes, 1682-1690. What is still missed is mostly noise around the key:

- digits still misread
- a decryption attached to the wrong coded line
- clerks writing a paraphrase rather than a letter-for-letter decryption

On volume 19/102 the decryptions are in very pale ink and are often misread or misplaced. The decoded text there still reads as German.

## Step 4. What changed in the key, and what did not work

- **The lists are alphabetical.** In C04, 95% of pairs in the word list (146-226) and 99% in the names list (250 and up) are in alphabetical order, with v-words before u-words: armee 255, bischof 260, Brandenburg 261, cron 284 ... Pohlen 331, Wien 346. Numbers 227-249 are a later supplement with no order (ein, dreissig, tausend, zwey, drey). So a missing value in the two lists must sort between its neighbours.
- **Fills by two independent looks.** For each number without a value, the places it occurs on the fit half were dealt into two separate sets. Gemini 4 Argon saw each set on its own: the decoded text around the number, the clerk's nearby decryption, and the two neighbours in the list. A value was kept only if both sets gave the same answer.
- **Testing the method.** 62 entries that C04 already has were hidden and put through the same procedure. Both sets agreed on 58, and 53 of those 58 matched C04 (91%). Three of the five misses are a longer form of the same word (ihr for ih, wie for wi, preussen for preussi). The other two disagree with C04: 210 came back as viel (C04 wider) and 226 as wur (C04 wer).
- **15 fills:** 148 an, 175 heit, 191 mich, 201 ohn, 213 uber, 230 zwischen, 233 zwey, 234 drey, 253 alliance, 254 ambassade, 269 churfurst, 275 conjun, 307 general, 323 moscau, 336 schwed.
- **6 weaker proposals:** 210 viel and 226 wur from the test above. 317 konig and 301 franckreich, because the clerk spells them that way. 312 hertzog, where the two sets gave herzog and hertzog. 295 ekm, which both sets read as the address Euer Königliche Majestät.
- **Fifteen numbers stay unknown** because the two sets did not agree.
- **Re-pairing the lines did not help.** Matching each decryption to the cipher anywhere on its page, not only the next two lines, scored 60.9% against 62.1% on the whole-page reading. Its shuffled control is 0.3%, so it is a sharper test, but pairing was not the gap.
- **More strips did not help.** An 11-strip pass over all of 19/102 with a majority vote of three readings changed 134 numbers and moved the fit half from 60.1% to 60.3%.
- **A language model alone does not work.** Choosing for each number the value under which the decode reads most like 17th-century German (a model built from 1,114 texts of 1600-1699 in the Deutsches Textarchiv) made the key worse and raised the shuffled score from 10% to 17%. A language model prefers common letters, not correct ones. The code is kept (`analysis/refine.py`) as a negative result.
- **What was withdrawn.** An earlier version added 28 entries and reported a held-out rise from 62.1% to 64.7%. That was not held out: the model proposing values was shown test-half examples. Daniel Bourdeau found the leak. All evidence for the current fills comes from the fit half.

## Step 5. The reading

`results/decoded.txt` is the mechanical decode: the plain German with each coded number replaced by its key value in brackets, and the clerk's decryptions on `G:` lines. It involves no judgement.

`results/decoded_original_key.txt` is the same mechanical decode with the original key on the re-read reading (Steps 6 and 7).

`results/reading.md` is a readable version of that decode, made by Gemini 4 Argon one half-page at a time, with Gemini 3.8 or 3.7 Flash where Argon returned nothing (228 of 229 half-pages with code, 67 of them by Flash). Nulls are left out. It joins the pieces into words and gives a one-line English summary. Coded passages are in {braces}, doubtful stretches in {?...?}. It was told not to add words, but it is a model's reading. Check anything that matters against `results/decoded_original_key.txt` and the page image. `results/overview.md` is a model-written summary of those one-line summaries, with page references.

## Step 6. The original key turns up

After the inferred key was published, the original was found in Riksarkivet's paper collection of cipher keys (Chifferklaver vol. 3, folder III:20, "Clavis Positiva et Resolutiva mit Resident Dörfler"). A scan of its two pages was ordered and transcribed by eye to `data/key_original.json`. It confirms Dudout's layout, gives a value to every number, and declares 1-13, 155 and everything from 349 up to be nulls, numbers put in to mean nothing.

Because nothing in it was fitted to the clerk's decryptions, it is a clean check on everything above.

| Key | Test half | Fresh lines | Shuffled key (test half) |
|---|---|---|---|
| TABLE-C04 as published | 71.6% | 73.0% | 10.5% |
| C04 + 15 fills + 6 proposals | 73.9% | 75.6% | 11.5% |
| Original 1680s key | 75.8% | 77.5% | 14.0% (best of 200: 16.6%) |

- **The inferred values mostly hold.** Of the 21 values found by the two-set method, 17 match the original, 3 differ only in spelling (ambassade for ambassad, ekm for ekmt, moscau for moscow) and 1 is wrong (148 is ation, not an). Both places where the method overruled C04 are right: 210 is viel and 226 is wür.
- **The original key adds only about two points.** It fixes 12 C04 values that were a different word, fills the 15 numbers the method could not agree on, and gives the full forms where C04 had short ones (dess for des, soll for sol). The gap that is left is not in the key.

## Step 7. Re-reading the doubtful digits

With the key settled, the next suspect was the digits. `analysis/numfix.py` found likely misreads without looking at any clerk decryption: each number was swapped for digits that look alike (8 and 0, 1 and 7, 3 and 5, and so on), and the swap was kept as a suspect if the decoded text around it read much more like 17th-century German. The 2,500 strongest suspects were cut from the full-size page and shown to Gemini 4 Argon twice, with no key and no decryptions and the two choices in swapped order. A digit was changed only when both answers agreed. That changed 244 numbers.

| Reading | Test half | Fresh lines |
|---|---|---|
| Newest reading, original key | 75.85% | 77.48% |
| After the re-read | 76.32% | 77.99% |
| Same number of random look-alike edits (30 tries) | 74.99% | 76.60% |

The re-read helps, and random edits hurt, so the method finds real misreads. But the gain is half a point. Most of what is still missed must come from the clerks: their spelling, their shorthand, and decryptions matched to the wrong coded line.

## What is still uncertain

- The original key was transcribed by one reader from scans. In this hand an e looks like an r, so the transcription was checked by zooming in, and one entry (344) is still marked uncertain.
- Volume 19/102 scores well under the others, because the clerk's ink is pale.
- The scores are a floor: a perfect key would not reach 100%, because the decryptions themselves are loose.
- One half-page (19/102 image 475, right half) has no readable version because Google's safety filter refuses the decoded text as a prompt, for Argon and Flash alike, even in 8-line pieces. Its decode is in `results/decoded_original_key.txt`.
- No one has yet read the whole decode against the images by eye.
