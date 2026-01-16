
import sys
import os
import json
from keyez.landing.spell_checker_advanced import check_spelling

def test_sent():
    text = "ខ្ញុំដើទៅផ្សារ"
    print(f"Input: {text}")
    result = check_spelling(text)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_sent()
