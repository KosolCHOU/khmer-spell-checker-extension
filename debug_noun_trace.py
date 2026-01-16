from keyez.landing.spell_checker_advanced import check_spelling

def debug():
    text = "ស្ដេច ឈឺ ដៃ ។"
    print(f"Checking: {text}")
    res = check_spelling(text)
    print(f"\nAll errors found:")
    for idx, err in res['errors'].items():
        print(f"  Index {idx}: {err}")
    
    print(f"\nExpected: Error on 'ដៃ' (should suggest 'ព្រះហស្ត')")

if __name__ == "__main__":
    debug()
