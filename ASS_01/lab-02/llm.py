import pandas as pd
from pydriller import Repository
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import csv
from tqdm import tqdm


REPO_PATH = "/home/set-iitgn-vm/Desktop/STT_lab_02/notepads"  # local clone of the repo
INPUT_CSV = "/home/set-iitgn-vm/Desktop/STT_lab_02/bugfix_commits.csv"
OUTPUT_CSV = "bugfix_commits_with_llm.csv"
MODEL_NAME = "mamiksik/CommitPredictorT5"
MAX_DIFF_CHARS = 500  # used ONLY for LLM input; full diff is still saved

print(f"Loading model {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)


def run_llm_inference(commit_msg: str, combined_diff_for_commit: str) -> str:
    # Keep LLM input compact for speed; output is a short “fix type” phrase
    short_diff = (combined_diff_for_commit or "")[:MAX_DIFF_CHARS]
    input_text = f"Commit message: {commit_msg}\nDiff: {short_diff}"
    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=64)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def extract_action(diff_text: str) -> str:
    if not diff_text:
        return "Modified file"
    d = diff_text.lower()
    if "+ if" in d and ("is not none" in d or "!= none" in d or "null" in d or " is not null" in d):
        return "Added null check"
    if "+ try" in d or "+ except" in d:
        return "Added exception handling"
    if "+ return" in d and "- return" in d:
        return "Modified return logic"
    if "+ assert" in d:
        return "Added assertion"
    if "+ log" in d or "+ logger" in d or "+ print" in d:
        return "Added logging"
    if "+ def " in d or "- def " in d:
        return "Modified function definition"
    if "+ raise " in d or "- raise " in d:
        return "Adjusted error raising"
    if "+ import " in d or "- import " in d:
        return "Changed imports"
    return "Modified logic"

def extract_component(diff_text: str) -> str:
    if not diff_text:
        return "unknown"
    for ln in diff_text.splitlines():
        if "def " in ln:
            try:
                return ln.split("def ", 1)[1].split("(", 1)[0].strip()
            except Exception:
                continue
        if ln.startswith("@@") and "def " in ln and "(" in ln:
            try:
                frag = ln.split("def ", 1)[1]
                name = frag.split("(", 1)[0].strip()
                if name:
                    return name
            except Exception:
                continue
    return "unknown"

def build_rectified_message(filename: str, original_msg: str, diff_text: str) -> str:
    action = extract_action(diff_text)
    component = extract_component(diff_text)
    return f"{action} in `{filename}` (function: `{component}`) — {original_msg}"


def main():
    commits_df = pd.read_csv(INPUT_CSV)
    target_hashes = commits_df["Hash"].dropna().astype(str).tolist()
    message_map = dict(zip(commits_df["Hash"].astype(str), commits_df["Message"].astype(str)))

    rows = []

    # Iterate commits with a progress bar
    repo_iter = Repository(REPO_PATH, only_commits=target_hashes).traverse_commits()
    for commit in tqdm(repo_iter, total=len(target_hashes), desc="Processing commits", unit="commit"):
        chash = str(commit.hash)
        cmsg = message_map.get(chash, commit.msg or "")

        # LLM once per commit on combined diff (keeps speed high)
        combined_diff = "\n".join([m.diff or "" for m in commit.modified_files])
        llm_fix_type = run_llm_inference(cmsg, combined_diff)

        # Per-file records with full sources and per-file diff
        for mod in commit.modified_files:
            filename = mod.new_path or mod.old_path or ""
            if not filename:
                continue

            source_before = mod.source_code_before or ""
            source_current = mod.source_code or ""
            diff_text = mod.diff or ""

            rectified = build_rectified_message(filename, cmsg, diff_text)

            rows.append({
                "Hash": chash,
                "Message": cmsg,
                "Filename": filename,
                "Source Code (before)": source_before,
                "Source Code (current)": source_current,
                "Diff": diff_text,
                "LLM Inference (fix type)": llm_fix_type,
                "Rectified Message": rectified
            })

    out_df = pd.DataFrame(rows, columns=[
        "Hash",
        "Message",
        "Filename",
        "Source Code (before)",
        "Source Code (current)",
        "Diff",
        "LLM Inference (fix type)",
        "Rectified Message"
    ])

    # Safe CSV writing for large diffs/source (quotes + escaping)
    out_df.to_csv(
        OUTPUT_CSV,
        index=False,
        quoting=csv.QUOTE_ALL,
        escapechar='\\'
    )

    print(f"Done. Wrote {len(out_df)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()

