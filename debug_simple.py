from keyez.landing.spell_checker_advanced import check_spelling

# Test if NOUN_LEVELS is accessible
from keyez.landing.spell_checker_advanced import SpellCheckerData

def debug():
    SpellCheckerData.build_tables()
    
    # Check if "ដៃ" is in the dictionary
    text = "ស្ដេច ឈឺ ដៃ ។"
    print(f"Checking: {text}")
    print(f"Testing word: 'ដៃ'")
    print(f"Hex: {'\u178a\u17c3'.encode('utf-8').hex()}")
    
    res = check_spelling(text)
    print(f"\nAll errors found:")
    for idx, err in res['errors'].items():
        print(f"  Index {idx}: {err}")

if __name__ == "__main__":
    debug()
