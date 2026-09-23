# Data

## Files
- `train.csv` — training set
- `val.csv` — validation set
- `test.csv` — test set
- `annotation_test.csv` — manual annotations for test set (150 words)
- `annotation_train.csv` — manual annotations for training set (150 words)

## Columns (train.csv / val.csv / test.csv)

| Column | Description |
|--------|-------------|
| `word` | Arabic word with diacritics (Tashkeel) |
| `phonemes` | Phoneme sequence, dash-separated (silver labels from parser) |
| `difficulty` | Phonological difficulty level: `low`, `medium`, or `high` |

## Columns (annotation_*.csv)

| Column | Description |
|--------|-------------|
| `word` | Arabic word with diacritics |
| `phonemes` | Parser-generated phoneme sequence (silver label) |
| `Annotator 1 (Gadi)` | Manual transcription by Taoufiq Gadi |
| `Annotator 2 (Sadouk)` | Manual transcription by Lamyaa Sadouk |

## Difficulty Scoring

Each word receives a difficulty score based on its phoneme sequence:
