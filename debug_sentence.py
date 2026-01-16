
from keyez.landing.spell_checker_advanced import segment_text

s = "កុមារត្រូវរៀនសូត្រពីកតញ្ញនិងការគោរពចាស់ទុំម"
print(f"'{s}' -> {segment_text(s)}")
