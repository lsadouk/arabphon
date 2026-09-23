# ArabPhon

Rule-based Arabic phoneme parser for Darija-influenced MSA text,
with LSTM seq2seq experiments using clean and noisy silver labels.

## Contents
- `parser/` — rule-based phoneme parser
- `data/` — train/val/test splits (CSV)
- `models/` — LSTM encoder-decoder (Exp 1 clean, Exp 2 noisy)
- `notebooks/` — training and evaluation notebooks

## Dataset
~[N] words with phoneme transcriptions and difficulty scores.
Annotated subset: 300 words (150 test + 150 train), κ = 0.99.

## Results
| Model | Exact Match | PER |
|-------|-------------|-----|
| Exp 1 (clean labels) | 78.0% | 5.37% |
| Exp 2 (noisy labels) | 77.8% | 4.49% |

## Citation
Sadouk, L., & Gadi, T. (under review). ArabPhon: A Rule-Based Arabic 
Phoneme Parser for Darija-Influenced MSA Text.

## Authors
Lamyaa Sadouk (EMSI Casablanca) · Taoufiq Gadi (MISI)
