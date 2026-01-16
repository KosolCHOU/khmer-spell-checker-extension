# Spell Checker Data Resources

This directory contains all the data files required for the advanced Khmer spell checker to function properly.

## Directory Structure

```
data/
├── dictionaries/       # Dictionary and reference data
│   ├── khmer-dictionary-2022.parquet
│   ├── khmer_word_frequency.csv
│   └── names.txt
├── models/            # Machine learning models
│   └── word_segmentation_model.pt
└── ngrams/            # N-gram data for contextual checking
    └── mobile-keyboard-data.csv
```

## File Descriptions

### Dictionaries (`data/dictionaries/`)

#### `khmer-dictionary-2022.parquet`
- **Size**: ~4.5 MB
- **Format**: Apache Parquet (columnar format)
- **Content**: Comprehensive Khmer dictionary with ~100k+ words
- **Columns**: 
  - `word`: Khmer word
  - `pos`: Part of speech (ន., កិ., គុ., គុណ., សព., ប., និ., ស.)
- **Source**: Khmer-Dictionary-2022 project
- **Usage**: Primary dictionary for spell checking and validation

#### `khmer_word_frequency.csv`
- **Size**: ~793 KB
- **Format**: CSV
- **Content**: Word frequency data with IPM (instances per million) scores
- **Columns**:
  - `word`: Khmer word
  - `ipm`: Frequency score (higher = more common)
- **Source**: SeaLang corpus
- **Usage**: Ranks correction suggestions by word frequency

#### `names.txt`
- **Size**: ~19 KB
- **Format**: Plain text (one name per line)
- **Content**: ~5,000+ Khmer personal names and proper nouns
- **Source**: khmerlbdict project
- **Usage**: Prevents common names from being flagged as spelling errors

### Models (`data/models/`)

#### `word_segmentation_model.pt`
- **Size**: ~26 MB
- **Format**: PyTorch model
- **Type**: BiLSTM (Bidirectional Long Short-Term Memory)
- **Purpose**: Word boundary detection for Khmer text segmentation
- **Source**: KhmerNLP project
- **Usage**: Currently optional (basic whitespace splitting used as fallback)
- **Note**: Can be integrated for improved segmentation of unsegmented text

### N-Grams (`data/ngrams/`)

#### `mobile-keyboard-data.csv`
- **Size**: ~4.5 MB
- **Format**: CSV
- **Content**: Frequency counts for 2-grams (bigrams) and 3-grams (trigrams)
- **Columns**:
  - Column 0: `word` (the phrase)
  - Column 1: `count` (frequency count)
  - Column 2: `ngram` (2 for bigram, 3 for trigram)
- **Source**: KhmerLang mobile keyboard data
- **Usage**: Contextual error detection based on word sequence likelihood

## Data Processing

The spell checker uses these files as follows:

1. **Dictionary Matching**: Checks if words are in the dictionary
2. **Frequency Scoring**: Ranks suggestions by how common they are
3. **Name Recognition**: Identifies proper nouns to avoid false positives
4. **Contextual Analysis**: Uses bigrams/trigrams to detect phrase-level errors
5. **Segmentation**: (Optional) Helps with word boundary detection

## File Sources

| File | Project | License | Link |
|------|---------|---------|------|
| khmer-dictionary-2022.parquet | Khmer Dictionary 2022 | Open | https://github.com/chhourn/khmer-dictionary |
| khmer_word_frequency.csv | SeaLang Corpus | Open | https://github.com/wannaphong/corpus |
| word_segmentation_model.pt | KhmerNLP | Open | https://github.com/soksim/KhmerNLP |
| mobile-keyboard-data.csv | KhmerLang | Open | https://github.com/khmerconlang/khmerlang-mobile-keyboard-data |
| names.txt | khmerlbdict | Open | https://github.com/khmerlang/khmerlbdict |

## Integration Notes

The spell checker (`spell_checker_advanced.py`) uses lazy loading for all data files:
- Files are loaded on first use
- Loaded data is cached in memory for performance
- Memory footprint: ~50-100 MB when fully loaded

## Updating Data

To update any data file:

1. Replace the file in the corresponding subdirectory
2. Clear the Python cache or restart the Django server
3. No code changes needed - the spell checker will automatically use the new data

## Performance Characteristics

- **Cold start**: ~5-10 seconds (initial data loading)
- **Subsequent checks**: <100ms per sentence
- **Memory usage**: ~100 MB for all data loaded
- **Concurrent requests**: Safe (data is read-only, no race conditions)

## Troubleshooting

If spell checking doesn't work:

1. **Check file existence**: Verify all files exist in this directory
2. **Check file permissions**: Ensure files are readable by the Django process
3. **Check file encoding**: Data files should be UTF-8 encoded
4. **Check logs**: Django logs will show which files fail to load

Example error message:
```
Warning: Could not load bigrams from .../ngrams/mobile-keyboard-data.csv
```

This means the file is missing or unreadable, but the spell checker will still work with basic dictionary checking.
