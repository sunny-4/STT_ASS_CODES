import pandas as pd
from collections import Counter
import os

# Load the CSV
df = pd.read_csv("bugfix_commits_with_llm.csv")

# 1. Total number of unique commits and total modified files
total_commits = df["Hash"].nunique()
total_files = len(df)

# 2. Average number of modified files per commit
avg_files_per_commit = total_files / total_commits if total_commits else 0

# 3. Distribution of fix types from LLM
fix_type_counts = df["LLM Inference (fix type)"].value_counts()

# 4. Most frequently modified filenames and extensions
filename_counts = df["Filename"].value_counts().head(10)
df["Extension"] = df["Filename"].apply(lambda x: os.path.splitext(x)[1])
extension_counts = df["Extension"].value_counts().head(10)

# Print results
print(f"Total unique commits: {total_commits}")
print(f"Total modified files: {total_files}")
print(f"Average files per commit: {avg_files_per_commit:.2f}\n")

print("Distribution of LLM Inference (fix type):")
print(fix_type_counts.to_string(), "\n")

print("Most frequently modified filenames:")
print(filename_counts.to_string(), "\n")

print("Most frequently modified file extensions:")
print(extension_counts.to_string())

