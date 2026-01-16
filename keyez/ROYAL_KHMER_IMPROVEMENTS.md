# Royal Khmer (Raja Sap) Stress Test & Improvements

## Overview
Enhanced the spell checker's ability to handle Royal Khmer (Raja Sap) by implementing semantic register mapping and fixing logic for compound verbs. Created a comprehensive stress test suite to verify correctness.

## Improvements Implemented

### 1. Semantic Register Mapping
**Problem**: The previous system arbitrarily suggested any royal verb (e.g., suggesting "Sroy" (Eat) for "Walk") because it lacked semantic awareness.
**Solution**: Implemented `SEMANTIC_REGISTER_MAP` in `spell_checker_constants.py` to map verbs by meaning.
- **Example**: 
    - `eat` -> Common: `ញ៉ាំ`, `ហូប` <-> Royal: `សោយ`, `ពិសា`
    - `go` -> Common: `ទៅ`, `ដើរ` <-> Royal: `យាង`, `ស្តេចយាង`
    - `sleep` -> Common: `ដេក` <-> Royal: `ផ្ទុំ`

### 2. Compound Royal Verb Support
**Problem**: The system flagged correct phrases like `សម្តេចយាងទៅ` because it saw `ទៅ` (Common) after `សម្តេច` (Royal).
**Solution**: Updated `detect_register_mismatch` to detect valid compound structures.
- Logic: If a common motion verb (`ទៅ`, `មក`) follows a royal motion verb (`យាង`), it is accepted as a directional particle.

### 3. Handling "Walk/Hangout" (ដើរលេង)
**Problem**: `សម្តេចដើរលេង` was not flagged because `ដើរលេង` is a single token not in the lookup map.
**Solution**: Added `ដើរលេង` to the `go` category in `SEMANTIC_REGISTER_MAP`.

## Stress Test Results (`stress_test_royal_khmer.py`)

✅ **Correct Royal Usage**: All pass.
- `សម្តេចយាងទៅព្រះវិហារ` -> Valid (No false positive)
- ` ` -> Valid

✅ **Correct Common Usage**: All pass.
- `ខ្ញុំញ៉ាំបាយ` -> Valid

✅ **Royal Subject + Common Verb Mismatch**: All pass.
- `សម្តេចដើរលេង` -> Suggests `យាង` / `យាងកម្សាន្ត`
- `ព្រះមហាក្សត្រញ៉ាំបាយ` -> Suggests `សោយ`
- `ព្រះករុណាទៅផ្សារ` -> Suggests `យាង`

✅ **Common Subject + Royal Verb Mismatch**: All pass.
- `ខ្ញុំសោយព្រះស្ងោយ` -> Suggests `ញ៉ាំ`
- `គាត់យាងទៅផ្ទះ` -> Suggests `ដើរ` / `ទៅ`

## Files Modified
1. `/home/kosol/AstroAI/keyez/landing/spell_checker_constants.py`: Added `SEMANTIC_REGISTER_MAP` and updated `go` variants.
2. `/home/kosol/AstroAI/keyez/landing/spell_checker_advanced.py`: Rewrote `detect_register_mismatch` to use semantic map & handle compounds.
3. `/home/kosol/AstroAI/keyez/stress_test_royal_khmer.py`: New test suite.
