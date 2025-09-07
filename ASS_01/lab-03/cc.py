import pandas as pd
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# ----------------------------
# CONFIG
# ----------------------------
INPUT_CSV = "/home/set-iitgn-vm/Desktop/STT_lab_03/bugfix_commits_with_llm.csv"
OUTPUT_CSV = "lab2_structural_metrics_first.csv"

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()

# Take only the first 100 rows
df = df.head(100)

# ----------------------------
# FUNCTION TO COMPUTE METRICS
# ----------------------------
def compute_metrics_row(row):
    def safe_metrics(code):
        if not isinstance(code, str) or code.strip() == "":
            return 0, 0, 0
        try:
            mi = mi_visit(code, True)
            cc = sum(c.complexity for c in cc_visit(code))
            loc = len(code.splitlines())
        except Exception:
            mi, cc, loc = 0, 0, 0
        return mi, cc, loc

    mi_b, cc_b, loc_b = safe_metrics(row["Source Code (before)"])
    mi_a, cc_a, loc_a = safe_metrics(row["Source Code (current)"])
    return mi_b, mi_a, cc_b, cc_a, loc_b, loc_a

# ----------------------------
# PARALLEL PROCESSING WITH PROGRESS
# ----------------------------
results = []
with Pool(cpu_count()) as pool:
    for res in tqdm(pool.imap(compute_metrics_row, [row for _, row in df.iterrows()]),
                    total=len(df), desc="Computing Structural Metrics"):
        results.append(res)

# ----------------------------
# UNPACK RESULTS
# ----------------------------
df["MI_Before"], df["MI_After"], df["CC_Before"], df["CC_After"], df["LOC_Before"], df["LOC_After"] = zip(*results)

# Compute changes
df["MI_Change"] = df["MI_After"] - df["MI_Before"]
df["CC_Change"] = df["CC_After"] - df["CC_Before"]
df["LOC_Change"] = df["LOC_After"] - df["LOC_Before"]

# Save updated dataset
df.to_csv(OUTPUT_CSV, index=False)
print(f"Done! Structural metrics for first 100 rows saved to '{OUTPUT_CSV}'.")

