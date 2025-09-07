import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
from nltk.translate.bleu_score import sentence_bleu
from tqdm import tqdm
import numpy as np

# ----------------------------
# CONFIG
# ----------------------------
INPUT_CSV = "lab2_structural_metrics_first.csv"
OUTPUT_CSV = "lab2_change_magnitude_metrics.csv"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ----------------------------
# LOAD DATA
# ----------------------------
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()

# ----------------------------
# LOAD CODEBERT MODEL
# ----------------------------
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")
model.to(DEVICE)
model.eval()

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def compute_semantic_similarity(code1, code2):
    """Compute cosine similarity between CodeBERT embeddings."""
    if not isinstance(code1, str):
        code1 = ""
    if not isinstance(code2, str):
        code2 = ""
    try:
        inputs1 = tokenizer(code1, return_tensors="pt", truncation=True, max_length=512).to(DEVICE)
        inputs2 = tokenizer(code2, return_tensors="pt", truncation=True, max_length=512).to(DEVICE)
        with torch.no_grad():
            emb1 = model(**inputs1).last_hidden_state.mean(dim=1)
            emb2 = model(**inputs2).last_hidden_state.mean(dim=1)
        cos_sim = torch.nn.functional.cosine_similarity(emb1, emb2).item()
    except Exception:
        cos_sim = 0.0
    return cos_sim

def compute_token_similarity(code1, code2):
    """Compute BLEU score between two code strings."""
    if not isinstance(code1, str):
        code1 = ""
    if not isinstance(code2, str):
        code2 = ""
    reference = [code1.split()]
    candidate = code2.split()
    try:
        score = sentence_bleu(reference, candidate)
    except Exception:
        score = 0.0
    return score

# ----------------------------
# COMPUTE METRICS WITH PROGRESS
# ----------------------------
semantic_sims = []
token_sims = []

for _, row in tqdm(df.iterrows(), total=len(df), desc="Computing Change Magnitude"):
    code_before = row["Source Code (before)"]
    code_after = row["Source Code (current)"]
    
    semantic_sims.append(compute_semantic_similarity(code_before, code_after))
    token_sims.append(compute_token_similarity(code_before, code_after))

# ----------------------------
# ADD TO DATAFRAME
# ----------------------------
df["Semantic_Similarity"] = semantic_sims
df["Token_Similarity"] = token_sims

# Save updated dataset
df.to_csv(OUTPUT_CSV, index=False)
print(f"Done! Change magnitude metrics saved to '{OUTPUT_CSV}'.")

