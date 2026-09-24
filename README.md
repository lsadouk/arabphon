# ArabPhon

Rule-based Arabic phoneme parser for Darija-influenced MSA text,
with LSTM seq2seq experiments using clean and noisy silver labels.

## Contents
- `parser/` — rule-based phoneme parser
- `data/` — train/val/test splits (CSV)
- `models/` — LSTM encoder-decoder (Exp 1 clean, Exp 2 noisy)
- `notebooks/` — training and evaluation notebooks

## Notebooks
- `arabphon_main.ipynb` — parser, dataset generation, LSTM training (Exp 1 & 2), evaluation
- `ArabPhon_LLM_Judge.ipynb` — GPT-4o qualitative evaluation (LLM-as-judge)
- `annotation.ipynb` — IAA computation (Cohen's kappa, parser accuracy)
  
## Dataset
~[N] words with phoneme transcriptions and difficulty scores.
Annotated subset: 250 words (150 test + 100 train), κ = 0.99.

## Results
| Model | Exact Match | PER |
|-------|-------------|-----|
| Exp 1 (clean labels) | 79.9% | 4.72% |
| Exp 2 (noisy labels) | 81.6%% | 3.87% |

## Citation
Sadouk, L., & Gadi, T. (under review). ArabPhon: A Rule-Based Arabic 
Phoneme Parser for Darija-Influenced MSA Text.

## Authors
Lamyaa Sadouk (EMSI Casablanca) · Taoufiq Gadi (MISI)
