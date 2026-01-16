
from keyez.landing.spell_checker_advanced import SpellCheckerData, segment_text, pos_tag_tokens, detect_error_slots

word_set, word_to_pos, word_freq, _ = SpellCheckerData.build_tables()
word_list = SpellCheckerData.get_word_list()
bigrams = {} # Keep it simple

s = "កុមារត្រូវរៀនសូត្រពីកតញ្ញនិងការគោរពចាស់ទុំម"
tokens = segment_text(s)
tagged = pos_tag_tokens(tuple(tokens), word_to_pos, word_set)
errors = {}
indices = detect_error_slots(tagged, word_set, word_list, bigrams, {}, errors, word_freq)

print(f"Tokens: {tokens}")
print(f"Indices: {indices}")
for idx in indices:
    print(f"Error at {idx}: {tagged[idx]['token']}")
