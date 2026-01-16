from keyez.landing.spell_checker_advanced import check_spelling

def debug():
    text = "ស្ដេច ឈឺ ដៃ ។"
    print(f"Checking: {text}")
    res = check_spelling(text)
    print(f"Result Errors: {res['errors']}")

if __name__ == "__main__":
    debug()
