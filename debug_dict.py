
from keyez.landing.spell_checker_advanced import SpellCheckerData, segment_text, pos_tag_tokens

word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()

test_strings = [
    "ចាស់ទុំម", "បូរាណណ", "មោះមុតត", "រូបភា"
]

for s in test_strings:
    tokens = segment_text(s)
    tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
    print(f"'{s}' -> {tagged}")
