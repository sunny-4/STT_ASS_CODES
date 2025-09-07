from pydriller import Repository
import csv

# 🔍 Keywords to identify bug-fixing commits
KEYWORDS = [
    'fix', 'fixed', 'fixes', 'fixing',
    'bug', 'bugs', 'bugfix', 'bugfixes',
    'error', 'errors', 'erroneous',
    'issue', 'issues', 'problem', 'problems',
    'defect', 'defects', 'fault', 'faults',
    'resolve', 'resolved', 'resolves', 'resolving',
    'patch', 'patched', 'patches',
    'correct', 'corrected', 'correction',
    'hotfix', 'hotfixes',
    'repair', 'repaired', 'recovery',
    'crash', 'crashes', 'crashing',
    'fail', 'fails', 'failed', 'failure',
    'exception', 'exceptions',
    'inconsistent', 'inconsistency',
    'unexpected', 'unintended',
    'regression', 'regressions',
    'typo', 'typos'
]


# 📁 Path to your local repo
REPO_PATH = '/home/set-iitgn-vm/Desktop/STT_lab_02/notepads'  # ← Replace this with your actual path

# 📄 Output CSV file
OUTPUT_FILE = 'bugfix_commits.csv'

def is_bugfix(message):
    message = message.lower()
    return any(keyword in message for keyword in KEYWORDS)

def extract_bugfix_commits():
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Hash', 'Message', 'Hashes of Parents', 'Is Merge Commit?', 'List of Modified Files'])

        for commit in Repository(REPO_PATH).traverse_commits():
            if is_bugfix(commit.msg):
                hash_ = commit.hash
                message = commit.msg
                parents = ' '.join(commit.parents)
                is_merge = len(commit.parents) > 1
                modified_files = [mod.filename for mod in commit.modified_files]
                writer.writerow([hash_, message, parents, is_merge, '; '.join(modified_files)])

    print(f"✅ Done! Bug-fixing commits saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_bugfix_commits()

