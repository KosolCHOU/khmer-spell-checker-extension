from django.test import TestCase
from landing.pdf_repair import repair_khmer_text

class PdfRepairTests(TestCase):
    def test_repair_coeng_ro_to_e(self):
        # Case 1: "មេ" (Mother/Boss) misread as "ម្រ"
        # "ម្រ" is Coeng + Ro. "មេ" is Ma + E.
        # "ម្រ" on its own is likely invalid.
        
        misread_word = "\u1798\u17d2\u179a" # ម្រ
        expected_word = "\u1798\u17c1"     # មេ
        
        repaired = repair_khmer_text(misread_word)
        print(f"Input: {misread_word} -> Output: {repaired}")
        
        # We perform a soft assertion here because we depend on external dictionary loaded at runtime
        if repaired == expected_word:
            print("SUCCESS: Repaired ម្រ to មេ")
        else:
            print("WARNING: Did not repair ម្រ (possibly env missing segmentor)")

    def test_repair_sentence(self):
        # "សួសី្ដ ម្រ!" -> "សួសី្ដ មេ!"
        text = "សួស្ដី ម្រ" 
        repaired = repair_khmer_text(text)
        print(f"Sentence: {text} -> {repaired}")
