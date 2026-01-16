import pandas as pd
import pickle
from pathlib import Path

# Paths
DATA_DIR = Path('landing/data')
DICT_PATH = DATA_DIR / "dictionaries" / "khmer-dictionary-2022.parquet"
FREQ_PATH = DATA_DIR / "dictionaries" / "khmer_word_frequency.csv"
NGRAM_PATH = DATA_DIR / "ngrams" / "mobile-keyboard-data.csv"

# 1. Load Dictionary
print("Loading dictionary...")
df_dict = pd.read_parquet(DICT_PATH)
# Convert to dict: word -> set of pos
word_to_pos = df_dict.groupby("word")["pos"].apply(set).to_dict()
word_set = set(df_dict["word"])

# 2. Load Frequency
print("Loading frequency...")
df_freq = pd.read_csv(FREQ_PATH)
word_freq_ipm = dict(zip(df_freq["word"], df_freq["ipm"]))
max_ipm = float(df_freq["ipm"].max())

# 3. Load Bigrams (limited to 50k as in original)
print("Loading bigrams...")
df_ngrams = pd.read_csv(NGRAM_PATH, header=None, usecols=[0, 1, 2], names=["word", "count", "ngram"])
df_bigrams = df_ngrams[df_ngrams["ngram"] == 2].sort_values("count", ascending=False).head(50000)

bigrams = {}
bigram_context_fwd = {}
bigram_context_bwd = {}

for row in df_bigrams.itertuples():
    phrase = str(row.word).strip()
    count = int(row.count)
    bigrams[phrase] = count
    parts = phrase.split()
    if len(parts) == 2:
        w1, w2 = parts[0], parts[1]
        if w1 not in bigram_context_fwd: bigram_context_fwd[w1] = []
        bigram_context_fwd[w1].append((w2, count))
        if w2 not in bigram_context_bwd: bigram_context_bwd[w2] = []
        bigram_context_bwd[w2].append((w1, count))

# Save bundle
bundle = {
    'word_set': word_set,
    'word_to_pos': word_to_pos,
    'word_freq_ipm': word_freq_ipm,
    'max_ipm': max_ipm,
    'bigrams': bigrams,
    'bigram_context_fwd': bigram_context_fwd,
    'bigram_context_bwd': bigram_context_bwd
}

bundle_path = DATA_DIR / "spell_checker_bundle.pkl"
with open(bundle_path, "wb") as f:
    pickle.dump(bundle, f, protocol=pickle.HIGHEST_PROTOCOL)

print(f"Bundle saved to {bundle_path}")
print(f"Bundle size: {bundle_path.stat().st_size / 1024 / 1024:.2f} MB")
