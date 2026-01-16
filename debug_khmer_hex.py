from keyez.landing.spell_checker_advanced import check_spelling
import json

# Manual NOUN_LEVELS just to compare hex
NOUN_LEVELS_TEST = {
    "បាយ": {3: "ចង្ហាន់", 4: "ព្រះស្ងោយ"},
    "ដៃ": {3: "ព្រះហស្ត", 4: "ព្រះហស្ត"},
}

def debug_hex():
    word_test = "ដៃ"
    print(f"Test word: '{word_test}' hex: {word_test.encode('utf-8').hex()}")
    
    for key in NOUN_LEVELS_TEST:
        print(f"Key in dict: '{key}' hex: {key.encode('utf-8').hex()} Match: {key == word_test}")

if __name__ == "__main__":
    debug_hex()
