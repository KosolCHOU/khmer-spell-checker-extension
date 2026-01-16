# Spell Checker System Improvements
## Based on Comprehensive Test Analysis

### Test Results Summary
- **test_spell_checker_comprehensive.py**: 98/114 passed (86% accuracy)
  - False Positives: 3
  - False Negatives: 13
  
- **test_spell_checker_heavy.py**: 89/100 passed (89% accuracy)
  - False Positives: 5
  - False Negatives: 6

---

## Critical Issues to Fix

### 1. False Negatives (Missed Errors) - HIGH PRIORITY

#### A. Contextual Word Confusion (Not Detected)
**Issue**: System fails to detect wrong word usage in context
- `នូវ` vs `នៅ` (object marker vs location)
- `ដែល` vs `ដែរ` (relative pronoun vs also)
- `ដ៏` vs `ដល់` (adjective marker vs to/reach)
- `នៃ` vs `ន័យ` (of vs meaning)
- `នាក់` vs `អ្នក` (classifier vs title)

**Solution**: Enhance contextual rules in `spell_checker_advanced.py`
- Add POS-based validation for these pairs
- Check surrounding words for context clues
- Implement pattern matching for common phrase structures

#### B. Missing Ending Characters
**Issue**: Words like `បា` (should be `បាយ`) not detected
**Solution**: 
- Add rule to check for incomplete words
- Validate against common word endings
- Check if adding common endings creates valid words

#### C. Honorific/Register Mismatch
**Issue**: Royal language mixed with common language not detected
- `សោយ` (royal) used with `ខ្ញុំ` (common)
- `ញ៉ាំ` (common) used with `ព្រះមហាក្សត្រ` (royal)

**Solution**:
- Implement register checking system
- Map words to their appropriate social register
- Flag mismatches between subject and verb registers

#### D. Archaic Spelling
**Issue**: Old spellings like `គំរោង` not flagged (should be `គម្រោង`)
**Solution**: Add to `COMMON_TYPOS` dictionary

#### E. Incomplete Words
**Issue**: `ការងា` (should be `ការងារ`) not detected
**Solution**: Check for common suffixes and validate completeness

---

### 2. False Positives (Incorrect Flags) - MEDIUM PRIORITY

#### A. Valid Complex Words Flagged
**Words incorrectly flagged**:
- `អច្ឆរិយៈ` (wonderful/marvelous)
- `សកលភាវូបនីយកម្ម` (globalization)
- `ហ្វ្រី` (free - loan word)
- `ៗ` (repetition mark in certain contexts)

**Solution**:
- Add these to `WHITELIST_WORDS`
- Improve compound word validation
- Add special handling for Khmer repetition mark `ៗ`

---

## Implementation Plan

### Phase 1: Quick Wins (Add to Constants)
1. **Update COMMON_TYPOS** with archaic spellings
2. **Update WHITELIST_WORDS** with false positives
3. **Add REGISTER_MAP** for honorific checking

### Phase 2: Contextual Rules Enhancement
1. Implement contextual validators for word pairs
2. Add POS-based context checking
3. Create pattern matchers for common phrases

### Phase 3: Advanced Features
1. Incomplete word detection
2. Register/honorific mismatch detection
3. Enhanced compound word validation

---

## Specific Code Changes Needed

### 1. spell_checker_constants.py

```python
# Add to COMMON_TYPOS
"គំរោង": "គម្រោង",
"ការងា": "ការងារ",

# Add to WHITELIST_WORDS
"អច្ឆរិយៈ", "សកលភាវូបនីយកម្ម", "ហ្វ្រី",

# New: Register mapping
REGISTER_MAP = {
    "ROYAL": {"សោយ", "យាង", "ទ្រង់", "ព្រះ"},
    "COMMON": {"ញ៉ាំ", "ទៅ", "គាត់", "ខ្ញុំ"},
    "FORMAL": {"បរិភោគ", "ធ្វើដំណើរ"},
}

ROYAL_SUBJECTS = {"ព្រះមហាក្សត្រ", "ព្រះករុណា", "សម្តេច"}
COMMON_SUBJECTS = {"ខ្ញុំ", "គាត់", "យើង", "អ្នក"}
```

### 2. spell_checker_advanced.py

Add new detection functions:
- `detect_register_mismatch()`
- `detect_incomplete_words()`
- `detect_contextual_confusion()`

---

## Expected Improvements

After implementing these changes:
- **Target Accuracy**: 95%+ on both test suites
- **False Positives**: Reduce to < 2%
- **False Negatives**: Reduce to < 3%

---

## Testing Strategy

1. Run both test suites after each phase
2. Track improvement metrics
3. Add new test cases for edge cases discovered
4. Validate no regression on existing passing tests
