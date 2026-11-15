# How the Dörffler code was read

Written for a reader with a college education and no background in codebreaking. Every number here was measured on the data in this repository.

## The material

Simon Dörffler was Sweden's resident diplomat at the Polish court in the 1680s. His despatches to King Charles XI are ordinary German letters. The sensitive parts switch into numbers, for example `218. 77. 53. 66. 25.`. Four volumes of these despatches are digitized by the Swedish National Archives (Riksarkivet, SE/RA/2115/I/19/100-103, about 2,170 page images, Public Domain Mark). 136 of those pages carry code: 2,209 coded lines and 26,070 numbers.

On many pages a clerk in Stockholm wrote the meaning of the numbers between the lines, in small pale German. We found 1,382 such decrypted lines. They are the answer key a historian would want, but they are incomplete, not word for word, and often hard to read. So they can test a codebook, but they do not replace one.

## The code

The code is a syllabary with a word list, the usual design for the period (historians call it a nomenclator). Brice Dudout (Europe chiffrée) worked out its layout and published a first table, TABLE-C04, in Dan Bourdeau's cyphersolver repository on 14 November 2026:

- 14-39 and 40-65: two alphabets, so each letter has two numbers
- 66-145: syllables, 16 consonants times 5 vowels (ba, be, bi, bo, bu, ...)
- 146-231: common words (der, die, und, von, nicht, ...)
- 250 and up: names and titles (König, Pohlen, Bischof, ...)

Dudout tested the table on three held-out pages and called all three tests failed, because they fell short of thresholds he set in advance. This repository tests the same table on much more material, and it holds up.

## Step 1. Read every coded page again, whole lines

Two AI models, Google's Gemini 4 Argon and Gemini 3.7 Flash, each read every coded half-page separately. Each read kept everything: the plain German, the numbers in place, and the clerk's decryption on its own tagged line above the numbers it explains. Where both models read a coded line (1,742 lines), their number sequences agree 89% on average. Where they disagree on a single number, both readings are kept.

## Step 2. A fair test

A key is good if decoding the numbers under a clerk's decryption gives back the clerk's letters. The score is the share of decryption letters that the decoding reproduces in order, counting only runs of three or more letters, because scattered single letters match by chance.

Chance is measured too. The same key with its entries shuffled among its numbers is scored 100-200 times. That shuffled score is what a meaningless key gets.

The pages were split before any key was changed:

- **Fit half:** volume 19/102, where the table was built, plus even-numbered pages of the other volumes.
- **Test half:** odd-numbered pages outside 19/102, 422 decryption lines and 14,245 letters. These are never used to change the key.

## Step 3. Results

| Key | Test half | Shuffled key |
|---|---|---|
| TABLE-C04 as published | 62.1% | 10.3% (best of 200: 13.8%) |
| Final key (this repository) | **64.7%** | 11.9% (best of 200: 14.6%) |

On every decryption line outside 19/102 that the table's authors never used (825 lines), TABLE-C04 alone scores 66.0%.

So the key is real. It works across all four volumes, 1682-1690, and it reproduces about two thirds of the clerk's letters, while a shuffled key reproduces about one tenth. The remaining third is mostly noise around the key, not errors in it:

- misread digits (for example 1/7, 3/8, 21/26)
- a decryption attached to the wrong coded line
- clerks writing a paraphrase rather than a letter-for-letter decryption

On volume 19/102 the decryptions are in very pale ink, and our readers often misplaced them. The score there is 42%, even on the pages the table was built from, while the decoded text itself reads as German.

## Step 4. What changed in the key, and what did not work

- **Votes from the clerk.** Where one number sits alone in a stretch the decoding gets wrong, the clerk's letters opposite it count as a vote. Only 3 entries changed, because the table was already about as good as the decryptions can confirm.
- **Filling the gaps.** About 100 numbers had no entry. For the 44 used five or more times, Gemini 4 Argon saw up to ten places each one occurs, with the decoding around it and the nearby decryption, and proposed a value. A proposal was kept only if it raised the score on the fit half. 25 were kept: for example 295 = "E. K. Mt." (Euer Königliche Majestät, the address to the king), 201 = Brandenburg, 253 = alliance, 266 = Bischof, 312 = Hertzog, 336 = Schwed(en). On the untouched test half, these fills raised the score from 62.0% to 64.2%. The others stay unknown.
- **A language model alone does not work.** We also tried improving the key by choosing, for each number, the value under which the decoded text reads most like 17th-century German. The model was built from 1,114 German texts of 1600-1699 in the Deutsches Textarchiv. It made the key worse on the test, 64.1% against 65.5%, and raised the shuffled score from 10% to 17%. A language model prefers common letters, not correct ones. The code is kept (`analysis/refine.py`) as a documented negative result.

## Step 4b. Re-checking disputed numbers against the image

The two readers disagreed on 2,019 single numbers. Gemini 4 Argon looked at each half-page again with every disputed number listed beside its neighbours, and picked one reading. It kept the first reader 1,571 times and switched to the second 448 times. The key was not used, so the test stays fair. The held-out score rose half a point, from 64.2% to 64.7%. Letting the key decide instead gave the same result to within 0.05 points. Disputed numbers are only 8% of the total, so they were never the main gap. The rest is the looseness of the clerk's decryptions, numbers both readers misread the same way, and the 2.6% of numbers with no value.

## Step 5. The reading

`results/decoded.txt` is the mechanical decode: the plain German with each coded number replaced by its key value in brackets, and the clerk's decryptions on `G:` lines. It involves no judgement.

`results/reading.md` is a readable version made by Gemini 4 Argon from the mechanical decode, one half-page at a time. It joins the pieces into words and gives a one-line English summary. Coded passages are in {braces}, doubtful stretches in {?...?}. It was told not to add words, but it is a model's reading. Check anything that matters against `decoded.txt` and the page image.

## What is still uncertain

- About 2.6% of the numbers have no key value. Most are rare, or fragments of numbers cut at the page fold.
- Single numbers are sometimes misread, and the key cannot fix those.
- The scores are a floor: a perfect key would not reach 100%, because the decryptions themselves are loose.
- No one has yet read the whole decode against the images by eye.
