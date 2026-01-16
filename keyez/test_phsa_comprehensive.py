#!/usr/bin/env python3
"""
Comprehensive test for ផ្សា vs ផ្សារ contextual spelling rules with full sentences
"""

import sys
sys.path.insert(0, '/home/kosol/AstroAI/keyez/landing')

from spell_checker_advanced import check_spelling

# Test cases with full sentences
test_sentences = [
    # Market context (should use ផ្សារ)
    ("ខ្ញុំទៅផ្សារទិញបន្លែ", "I go to the market to buy vegetables"),
    ("គាត់នៅផ្សារលក់ផ្លែឈើ", "He is at the market selling fruits"),
    ("ផ្សារដែកនៅភ្នំពេញ", "The iron market in Phnom Penh"),
    ("ផ្សារកញ្ចក់មានទំនិញច្រើន", "The glass market has many goods"),
    
    # Sting/spicy context (should use ផ្សា)
    ("ម្ហូបនេះផ្សាណាស់", "This food is very spicy/stinging"),
    ("ភ្នែកខ្ញុំផ្សាពេលកាត់ខ្ទឹមបារាំង", "My eyes sting when cutting onions"),
    ("របួសនេះឈឺផ្សា", "This wound hurts/stings"),
    ("ឈឺផ្សាខ្លាំង", "It stings/hurts a lot"),
    
    # Incorrect usage (should be corrected)
    ("ខ្ញុំទៅផ្សាទិញបន្លែ", "Wrong: should be ផ្សារ (market)"),
    ("គាត់នៅផ្សាលក់ផ្លែឈើ", "Wrong: should be ផ្សារ (market)"),
    ("ផ្សាដែកនៅភ្នំពេញ", "Wrong: should be ផ្សារ (iron market)"),
    ("ផ្សាកញ្ចក់មានទំនិញច្រើន", "Wrong: should be ផ្សារ (glass market)"),
    ("ភ្នែកខ្ញុំផ្សារពេលកាត់ខ្ទឹមបារាំង", "Wrong: should be ផ្សា (sting)"),
    ("របួសនេះឈឺផ្សារ", "Wrong: should be ផ្សា (sting)"),
]

print("Comprehensive test for ផ្សា vs ផ្សារ in full sentences")
print("=" * 70)

for text, description in test_sentences:
    result = check_spelling(text)
    errors_dict = result.get('errors', {})
    
    # Filter only ផ្សា/ផ្សារ related errors
    phsa_errors = {idx: err for idx, err in errors_dict.items() 
                   if err['original'] in ['ផ្សា', 'ផ្សារ']}
    
    print(f"\nSentence: {text}")
    print(f"Meaning: {description}")
    
    if phsa_errors:
        print(f"✓ ផ្សា/ផ្សារ errors detected: {len(phsa_errors)}")
        for idx, error in phsa_errors.items():
            print(f"  - '{error['original']}' → '{error.get('suggestions', [])[0] if error.get('suggestions') else 'N/A'}'")
            print(f"    Rule: {error.get('type', 'N/A')}")
    else:
        print("✗ No ផ្សា/ផ្សារ errors detected")

print("\n" + "=" * 70)
print("Test completed!")
