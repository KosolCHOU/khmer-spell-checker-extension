"""
Test script for the Khmer Segmenter Module
Demonstrates how to use the separated segmentation functions for debugging.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from landing.khmer_segmenter import (
    normalize_text,
    segment_text,
    debug_segment,
    is_kh_consonant,
    is_kh_letter_seq
)
from landing.spell_checker_advanced import SpellCheckerData


def test_segmentation(text: str):
    """Test segmentation with detailed output"""
    print(f"\n{'='*80}")
    print(f"Testing: {text}")
    print(f"{'='*80}")
    
    # Load data
    word_set, _, word_freq, _ = SpellCheckerData.build_tables()
    words_by_start = SpellCheckerData.get_words_by_start()
    
    # Simple is_known function for testing
    def is_known(token: str) -> bool:
        return token in word_set
    
    # Get debug information
    debug_info = debug_segment(text, word_set, word_freq, words_by_start, is_known)
    
    # Print results
    print(f"\n1. Normalized Text:")
    print(f"   {debug_info['normalized']}")
    
    print(f"\n2. Viterbi Tokens ({len(debug_info['viterbi_tokens'])} tokens):")
    print(f"   {debug_info['viterbi_tokens']}")
    
    print(f"\n3. After Merging Unknown ({len(debug_info['merged_tokens'])} tokens):")
    print(f"   {debug_info['merged_tokens']}")
    
    print(f"\n4. Final Tokens ({len(debug_info['final_tokens'])} tokens):")
    print(f"   {debug_info['final_tokens']}")
    
    print(f"\n5. Statistics:")
    for key, value in debug_info['stats'].items():
        print(f"   {key}: {value}")
    
    print(f"\n6. Unknown Tokens:")
    unknown = debug_info['stats']['unknown_tokens']
    if unknown:
        for token in unknown:
            print(f"   - '{token}'")
    else:
        print(f"   (none)")


def main():
    """Run tests"""
    print("Khmer Segmenter Test Suite")
    print("="*80)
    
    # Test cases
    test_cases = [
        "សូមស្វាគមន៍",  # Welcome
        "ការសិក្សា",      # Study/Education
        "កាទឹក",          # Water glass (compound)
        "ខ្ញុំចង់ទៅផ្សារ",  # I want to go to market
    ]
    
    for text in test_cases:
        test_segmentation(text)
    
    print(f"\n{'='*80}")
    print("Tests completed!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
