#!/usr/bin/env python
"""
Quick Segmentation Debugger
Usage: python debug_seg.py "ខ្ញុំចង់ទៅផ្សារ"
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from landing.khmer_segmenter import debug_segment
from landing.spell_checker_advanced import SpellCheckerData


def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_seg.py \"<khmer_text>\"")
        print("\nExample:")
        print("  python debug_seg.py \"ខ្ញុំចង់ទៅផ្សារ\"")
        sys.exit(1)
    
    text = sys.argv[1]
    
    print(f"\n{'='*80}")
    print(f"Debugging Segmentation for: {text}")
    print(f"{'='*80}\n")
    
    # Load data
    print("Loading dictionary data...")
    word_set, _, word_freq, _ = SpellCheckerData.build_tables()
    words_by_start = SpellCheckerData.get_words_by_start()
    
    def is_known(token: str) -> bool:
        return token in word_set
    
    # Debug
    print("Running segmentation...\n")
    debug_info = debug_segment(text, word_set, word_freq, words_by_start, is_known)
    
    # Display results
    print(f"📝 Normalized Text:")
    print(f"   '{debug_info['normalized']}'")
    print()
    
    print(f"🔍 Viterbi Tokens ({len(debug_info['viterbi_tokens'])} tokens):")
    for i, token in enumerate(debug_info['viterbi_tokens'], 1):
        known = "✓" if is_known(token) else "✗"
        print(f"   {i}. '{token}' {known}")
    print()
    
    print(f"🔗 After Merging Unknown ({len(debug_info['merged_tokens'])} tokens):")
    for i, token in enumerate(debug_info['merged_tokens'], 1):
        known = "✓" if is_known(token) else "✗"
        print(f"   {i}. '{token}' {known}")
    print()
    
    print(f"✅ Final Tokens ({len(debug_info['final_tokens'])} tokens):")
    for i, token in enumerate(debug_info['final_tokens'], 1):
        known = "✓" if is_known(token) else "✗"
        print(f"   {i}. '{token}' {known}")
    print()
    
    print(f"📊 Statistics:")
    stats = debug_info['stats']
    print(f"   Original length: {stats['original_length']} chars")
    print(f"   Normalized length: {stats['normalized_length']} chars")
    print(f"   Viterbi tokens: {stats['viterbi_token_count']}")
    print(f"   After merging: {stats['merged_unknown_count']}")
    print(f"   Final tokens: {stats['final_token_count']}")
    print()
    
    unknown = stats['unknown_tokens']
    if unknown:
        print(f"⚠️  Unknown Tokens ({len(unknown)}):")
        for token in unknown:
            print(f"   - '{token}'")
    else:
        print(f"✓ All tokens are known words!")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
