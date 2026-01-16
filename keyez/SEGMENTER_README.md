# Khmer Segmenter Module

## Overview

The Khmer text segmentation functionality has been extracted from `spell_checker_advanced.py` into a separate module `khmer_segmenter.py` for easier debugging and maintenance.

## Files

### `landing/khmer_segmenter.py`
Contains all text segmentation logic:
- **Text Normalization**: `normalize_text()`
- **Character Type Checking**: `is_kh_consonant()`, `is_kh_letter_seq()`
- **Viterbi Segmentation**: `viterbi_segment()`, `get_char_type_cost()`
- **Main Segmentation**: `segment_text()`
- **Debugging**: `debug_segment()`

### `landing/spell_checker_advanced.py`
Updated to import segmentation functions from `khmer_segmenter.py` instead of defining them locally.

### `test_segmenter.py`
Test script demonstrating how to use the segmenter module for debugging.

## Usage

### Basic Segmentation

```python
from landing.khmer_segmenter import segment_text
from landing.spell_checker_advanced import SpellCheckerData

# Load dictionary data
word_set, _, word_freq, _ = SpellCheckerData.build_tables()
words_by_start = SpellCheckerData.get_words_by_start()

# Define is_known function
def is_known(token: str) -> bool:
    return token in word_set

# Segment text
text = "សូមស្វាគមន៍"
tokens = segment_text(text, word_set, word_freq, words_by_start, is_known)
print(tokens)
```

### Debug Segmentation

```python
from landing.khmer_segmenter import debug_segment

# Get detailed segmentation information
debug_info = debug_segment(text, word_set, word_freq, words_by_start, is_known)

print("Normalized:", debug_info['normalized'])
print("Viterbi tokens:", debug_info['viterbi_tokens'])
print("Merged tokens:", debug_info['merged_tokens'])
print("Final tokens:", debug_info['final_tokens'])
print("Statistics:", debug_info['stats'])
```

### Running Tests

```bash
cd /home/kosol/AstroAI/keyez
python test_segmenter.py
```

## Benefits

1. **Easier Debugging**: Segmentation logic is now isolated and can be tested independently
2. **Better Organization**: Clear separation of concerns between segmentation and spell checking
3. **Reusability**: Segmentation functions can be used by other modules
4. **Debug Tools**: `debug_segment()` provides detailed information about each segmentation step

## Migration Notes

The `segment_text()` function signature has changed:

**Old (in spell_checker_advanced.py)**:
```python
@lru_cache(maxsize=512)
def segment_text(text: str) -> List[str]:
    # ... implementation
```

**New (in khmer_segmenter.py)**:
```python
def segment_text(text: str, word_set: Set[str], word_freq: Dict[str, float], 
                 words_by_start: Dict[str, List[str]], is_known_func) -> List[str]:
    # ... implementation
```

The spell checker now passes the required parameters explicitly when calling `segment_text()`.

## Debugging Tips

1. Use `debug_segment()` to see the step-by-step segmentation process
2. Check the `unknown_tokens` in the statistics to identify problematic words
3. Compare `viterbi_tokens` vs `final_tokens` to understand merging behavior
4. Use the test script to quickly test specific text samples

## Future Improvements

- Add caching mechanism for frequently segmented texts
- Implement prefix tree (trie) for faster word lookup
- Add more detailed logging options
- Create visualization tools for segmentation results
