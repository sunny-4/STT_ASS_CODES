import pandas as pd

# Load your existing CSV
df = pd.read_csv("/home/student/Desktop/stt_lab_04/commits_data.csv")

# Add discrepancy column (ignoring whitespace and newlines)
df["Discrepancy"] = df.apply(
    lambda row: "Yes" if str(row["diff_meyers"]).strip().replace(" ", "") != str(row["diff_histogram"]).strip().replace(" ", "") else "No",
    axis=1
)

# Save updated CSV
df.to_csv("commits_data_with_discrepancy.csv", index=False, encoding="utf-8")

print("✅ New CSV saved as commits_data_with_discrepancy.csv")
print("Total mismatches:", (df["Discrepancy"] == "Yes").sum())
print("Total matches:", (df["Discrepancy"] == "No").sum())

