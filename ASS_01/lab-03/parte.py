import pandas as pd

INPUT_CSV = "lab2_change_magnitude_metrics.csv"
OUTPUT_CSV = "lab2_classification.csv"

# Thresholds (adjustable)
SEMANTIC_THRESHOLD = 0.80
TOKEN_THRESHOLD = 0.75

df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()

df["Semantic_class"] = df["Semantic_Similarity"].apply(
    lambda x: "Minor" if x >= SEMANTIC_THRESHOLD else "Major"
)

# Token classification
df["Token_class"] = df["Token_Similarity"].apply(
    lambda x: "Minor" if x >= TOKEN_THRESHOLD else "Major"
)

# Check agreement
df["Classes_Agree"] = df.apply(
    lambda row: "YES" if row["Semantic_class"] == row["Token_class"] else "NO", axis=1
)

df.to_csv(OUTPUT_CSV, index=False)
print(f"Done! Classification saved to '{OUTPUT_CSV}'.")

