"""
Quick test to verify spell checker still works after segmentation refactoring
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from landing.spell_checker_advanced import check_spelling


def test_spell_checker():
    """Test that spell checker works with the new segmenter module"""
    
    print("Testing Spell Checker with Segmenter Module")
    print("="*80)
    
    # Test cases
    test_cases = [
        ("សូមស្វាគមន៍", "Correct text - should have no errors"),
        ("ការសិក្សា", "Correct text - should have no errors"),
        ("កាទឹក", "Compound word - should be recognized"),
        ("សូមស្វាគមន", "Missing final character - should detect error"),
    ]
    
    for text, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Input: {text}")
        
        try:
            result = check_spelling(text)
            
            if result['errors']:
                print(f"✗ Errors found: {len(result['errors'])}")
                for idx, error in result['errors'].items():
                    print(f"  - Position {idx}: {error['original']}")
                    if error.get('suggestions'):
                        print(f"    Suggestions: {error['suggestions'][:3]}")
            else:
                print(f"✓ No errors detected")
                
        except Exception as e:
            print(f"✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("Test completed!")


if __name__ == "__main__":
    test_spell_checker()
