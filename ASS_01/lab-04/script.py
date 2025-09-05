# python script
from pydriller import Repository
import pandas as pd

repo_list = [
    "https://github.com/4paradigm/openmldb",
    "https://github.com/aappleby/metroboy",
    "https://github.com/aardappel/lobster"
]

# 1) Pre-pass: collect histogram diffs for (repo, commit, paths)
hist_map = {}
for i in repo_list:
    print(f"[INFO] Starting histogram diff collection for {i}...")
    commit_count = 0
    for commit in Repository(i, skip_whitespaces=True, histogram_diff=True).traverse_commits():
        if commit_count >= 500:
            break
        for m in commit.modified_files:
            key = (i, commit.hash, m.old_path, m.new_path)
            hist_map[key] = m.diff
        commit_count += 1
    print(f"[DONE] Histogram diff collection completed for {i} ({commit_count} commits).")

# 2) Your original pass (Myers is the default)
rows = []
for i in repo_list:
    print(f"[INFO] Starting Myers diff collection for {i}...")
    commit_count = 0
    for commit in Repository(i, skip_whitespaces=True).traverse_commits():
        if commit_count >= 500:
            break
        for m in commit.modified_files:
            key = (i, commit.hash, m.old_path, m.new_path)
            row = {
                "old_path": m.old_path,
                "new_path": m.new_path,
                "commit_SHA": commit.hash,
                "parent_SHA": commit.parents[0] if len(commit.parents) > 0 else None,
                "commit_message": commit.msg,
                "diff_meyers": m.diff,
                "diff_histogram": hist_map.get(key)
            }
            rows.append(row)
        commit_count += 1
    print(f"[DONE] Myers diff collection completed for {i} ({commit_count} commits).")

df = pd.DataFrame(rows)
output_file = "/home/student/Desktop/commits_data.csv"
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"[SUCCESS] Data written to {output_file}")
