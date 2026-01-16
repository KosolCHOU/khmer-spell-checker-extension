
from keyez.landing.spell_checker_advanced import segment_text

test_strings = [
    "ស្អាណាស់",
    "ផ្ញើរពត៌មាន",
    "សុវត្ថិភានៅ",
    "ចាស់ទុំម",
    "បូរាណណ",
    "មោះមុតត",
    "គោរពនៅវិន័យ",
    "រាល់ឆ្មាំ"
]

for s in test_strings:
    print(f"'{s}' -> {segment_text(s)}")
