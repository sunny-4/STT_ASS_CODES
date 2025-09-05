import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset with discrepancy column
df = pd.read_csv(r"C:\Users\mamil\Downloads\stt_lab_04\stt_lab_04\commits_data_with_discrepancy.csv")

# Only count mismatches
mismatches = df[df["Discrepancy"] == "Yes"]

# Function to categorize file types
def categorize_file(path):
    if pd.isna(path):   # if file path is missing
        return "Other"
    path = path.lower()
    if "test" in path or path.endswith("_test.py") or path.startswith("test_"):
        return "Test Code"
    elif path.endswith((".py", ".java", ".c", ".cpp")):
        return "Source Code"
    elif "readme" in path:
        return "README"
    elif "license" in path or path.strip() == "license":   # handle LICENSE file
        return "LICENSE"
    else:
        return "Other"

# Apply categorization (use new_path if available, otherwise old_path)
mismatches["File_Type"] = mismatches.apply(
    lambda row: categorize_file(row["new_path"] if pd.notna(row["new_path"]) else row["old_path"]), axis=1
)

# Count mismatches per category
stats = mismatches["File_Type"].value_counts()

# Ensure all categories appear in the plot (even if 0)
all_categories = ["Source Code", "Test Code", "README", "LICENSE", "Other"]
stats = stats.reindex(all_categories, fill_value=0)

print("Mismatch Statistics:")
print(stats)

# Plot results
plt.figure(figsize=(6, 6))
stats.plot(kind="bar", color="skyblue", edgecolor="black")
plt.title("Mismatch Counts by File Type")
plt.xlabel("File Type")
plt.ylabel("# of Mismatches")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
