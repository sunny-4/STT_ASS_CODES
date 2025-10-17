import pandas as pd
import matplotlib.pyplot as plt

INPUT_CSV = "bugfix_commits_with_llm.csv"   
def is_precise(msg: str, diff: str, filename: str) -> bool:
    if not isinstance(msg, str) or not msg.strip():
        return False
    words = msg.lower().split()
    if len(words) < 3:  
        return False
    fname = (filename or "").lower()
    if any(token in msg.lower() for token in fname.replace("/", " ").split()):
        return True
    diff_keywords = ["null", "check", "log", "return", "assert", "exception", "import"]
    if any(kw in msg.lower() for kw in diff_keywords):
        return True
    return False

def main():
    df = pd.read_csv(INPUT_CSV)

    df["DevPrecise"]  = df.apply(lambda r: is_precise(r["Message"], r["Diff"], r["Filename"]), axis=1)
    df["LLMPrecise"]  = df.apply(lambda r: is_precise(r["LLM Inference (fix type)"], r["Diff"], r["Filename"]), axis=1)
    df["RectPrecise"] = df.apply(lambda r: is_precise(r["Rectified Message"], r["Diff"], r["Filename"]), axis=1)

    rq1 = df["DevPrecise"].mean()
    rq2 = df["LLMPrecise"].mean()
    rq3 = df["RectPrecise"].mean()

    print("RQ1 (Developer hit rate):", rq1)
    print("RQ2 (LLM hit rate):", rq2)
    print("RQ3 (Rectifier hit rate):", rq3)

    # Plot
    scores = [rq1, rq2, rq3]
    labels = ["RQ1: Developer", "RQ2: LLM", "RQ3: Rectifier"]

    plt.bar(labels, scores, color=["blue", "green", "orange"])
    plt.ylim(0, 1)
    plt.ylabel("Hit Rate")
    plt.title("Commit Message Precision Evaluation")
    plt.show()

if __name__ == "__main__":
    main()
