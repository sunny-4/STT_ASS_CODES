import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations

# ============================================================================
# STEP 1: Load the consolidated CSV file
# ============================================================================
print("Loading consolidated CSV file...")
# Update this path to your CSV file
csv_file = "consolidated_cwe_findings.csv"
df = pd.read_csv(csv_file)

# Display basic info about the data
print(f"\nLoaded {len(df)} records")
print(f"Columns: {df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head())

# ============================================================================
# STEP 2: Extract unique CWE IDs for each tool
# ============================================================================
print("\n" + "="*80)
print("EXTRACTING UNIQUE CWE IDs PER TOOL")
print("="*80)

# Get unique tool names
tools = df['Tool_name'].unique()
print(f"\nTools found: {tools}")

# Create a dictionary to store CWE sets for each tool
tool_cwes = {}

for tool in tools:
    # Get all CWE IDs detected by this tool (across all projects)
    tool_data = df[df['Tool_name'] == tool]
    cwe_ids = set(tool_data['CWE_ID'].unique())
    tool_cwes[tool] = cwe_ids
    print(f"\n{tool}:")
    print(f"  - Unique CWEs detected: {len(cwe_ids)}")
    print(f"  - CWE IDs: {sorted(cwe_ids)[:10]}..." if len(cwe_ids) > 10 else f"  - CWE IDs: {sorted(cwe_ids)}")

# ============================================================================
# STEP 3: Compute IoU (Jaccard Index) for each tool pair
# ============================================================================
print("\n" + "="*80)
print("COMPUTING PAIRWISE IoU (JACCARD INDEX)")
print("="*80)

def compute_iou(set1, set2):
    """
    Compute Intersection over Union (Jaccard Index)
    IoU = |A ∩ B| / |A ∪ B|
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0

# Create IoU matrix
n_tools = len(tools)
iou_matrix = np.zeros((n_tools, n_tools))

print("\nComputing IoU for each tool pair:")
for i, tool1 in enumerate(tools):
    for j, tool2 in enumerate(tools):
        if i == j:
            iou_matrix[i][j] = 1.0  # IoU with itself is 1
        else:
            iou = compute_iou(tool_cwes[tool1], tool_cwes[tool2])
            iou_matrix[i][j] = iou
            if i < j:  # Print only once for each pair
                intersection = tool_cwes[tool1].intersection(tool_cwes[tool2])
                union = tool_cwes[tool1].union(tool_cwes[tool2])
                print(f"\n{tool1} vs {tool2}:")
                print(f"  - IoU: {iou:.4f}")
                print(f"  - Intersection: {len(intersection)} CWEs")
                print(f"  - Union: {len(union)} CWEs")

# ============================================================================
# STEP 4: Create Tool × Tool IoU Matrix DataFrame
# ============================================================================
print("\n" + "="*80)
print("TOOL × TOOL IoU MATRIX")
print("="*80)

iou_df = pd.DataFrame(iou_matrix, index=tools, columns=tools)
print("\n", iou_df.round(4))

# Save to CSV
output_file = "iou_matrix.csv"
iou_df.to_csv(output_file)
print(f"\nIoU matrix saved to: {output_file}")

# ============================================================================
# STEP 5: Visualize IoU Matrix as Heatmap
# ============================================================================
print("\n" + "="*80)
print("GENERATING VISUALIZATIONS")
print("="*80)

plt.figure(figsize=(10, 8))
sns.heatmap(iou_df, annot=True, fmt='.3f', cmap='RdYlGn', 
            vmin=0, vmax=1, square=True, linewidths=0.5,
            cbar_kws={'label': 'IoU (Jaccard Index)'})
plt.title('Tool × Tool IoU Matrix\n(Intersection over Union of CWE IDs)', 
          fontsize=14, fontweight='bold')
plt.xlabel('Tools', fontsize=12)
plt.ylabel('Tools', fontsize=12)
plt.tight_layout()
plt.savefig('iou_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Heatmap saved as: iou_heatmap.png")
plt.show()

# ============================================================================
# STEP 6: Analyze and Interpret Results
# ============================================================================
print("\n" + "="*80)
print("INSIGHTS AND INTERPRETATION")
print("="*80)

# Average IoU (excluding diagonal)
off_diagonal_values = []
for i in range(n_tools):
    for j in range(i+1, n_tools):
        off_diagonal_values.append(iou_matrix[i][j])

avg_iou = np.mean(off_diagonal_values)
print(f"\n1. OVERALL SIMILARITY")
print(f"   Average IoU across all tool pairs: {avg_iou:.4f}")

if avg_iou < 0.3:
    print("   → High diversity: Tools detect largely different CWE categories")
elif avg_iou < 0.6:
    print("   → Moderate diversity: Tools have some overlap but also unique detections")
else:
    print("   → High similarity: Tools detect similar CWE categories")

# Find most similar and most diverse pairs
print(f"\n2. TOOL PAIR ANALYSIS")
max_iou = 0
min_iou = 1
max_pair = None
min_pair = None

for i in range(n_tools):
    for j in range(i+1, n_tools):
        if iou_matrix[i][j] > max_iou:
            max_iou = iou_matrix[i][j]
            max_pair = (tools[i], tools[j])
        if iou_matrix[i][j] < min_iou:
            min_iou = iou_matrix[i][j]
            min_pair = (tools[i], tools[j])

print(f"\n   Most Similar Pair: {max_pair[0]} & {max_pair[1]}")
print(f"   - IoU: {max_iou:.4f}")
print(f"   - Interpretation: These tools have the highest overlap in detected CWEs")

print(f"\n   Most Diverse Pair: {min_pair[0]} & {min_pair[1]}")
print(f"   - IoU: {min_iou:.4f}")
print(f"   - Interpretation: These tools detect mostly different CWE categories")

# Maximum coverage analysis
print(f"\n3. MAXIMUM CWE COVERAGE ANALYSIS")
max_coverage = 0
best_combination = None

# Check all possible combinations
for r in range(1, n_tools + 1):
    for combo in combinations(tools, r):
        # Union of all CWEs from tools in this combination
        combined_cwes = set()
        for tool in combo:
            combined_cwes.update(tool_cwes[tool])
        
        if len(combined_cwes) > max_coverage:
            max_coverage = len(combined_cwes)
            best_combination = combo

print(f"\n   Best Tool Combination: {', '.join(best_combination)}")
print(f"   - Total unique CWEs covered: {max_coverage}")
print(f"   - Interpretation: This combination maximizes CWE coverage")

# Individual tool coverage
print(f"\n4. INDIVIDUAL TOOL COVERAGE")
for tool in sorted(tools, key=lambda t: len(tool_cwes[t]), reverse=True):
    print(f"   {tool}: {len(tool_cwes[tool])} unique CWEs")

# Complementarity analysis
print(f"\n5. COMPLEMENTARITY ANALYSIS")
for i, tool1 in enumerate(tools):
    for j, tool2 in enumerate(tools):
        if i < j:
            unique_to_tool1 = tool_cwes[tool1] - tool_cwes[tool2]
            unique_to_tool2 = tool_cwes[tool2] - tool_cwes[tool1]
            print(f"\n   {tool1} vs {tool2}:")
            print(f"   - Unique to {tool1}: {len(unique_to_tool1)} CWEs")
            print(f"   - Unique to {tool2}: {len(unique_to_tool2)} CWEs")
            if len(unique_to_tool1) > 10 or len(unique_to_tool2) > 10:
                print(f"   → High complementarity: Using both tools is beneficial")

# ============================================================================
# STEP 7: Create Summary Report
# ============================================================================
print("\n" + "="*80)
print("KEY TAKEAWAYS")
print("="*80)

print("""
Based on the Jaccard Index (IoU) analysis:

1. TOOL SIMILARITY vs DIVERSITY
   - Low IoU values (<0.3) indicate tools focus on different vulnerability types
   - High IoU values (>0.7) suggest significant overlap in detection capabilities
   
2. IMPLICATIONS FOR TOOL SELECTION
   - Choose tools with LOW IoU for maximum coverage (complementary tools)
   - Tools with HIGH IoU may be redundant for the same project
   
3. COVERAGE OPTIMIZATION
   - The best tool combination identified maximizes unique CWE coverage
   - Consider using multiple diverse tools in production environments
   
4. TOOL STRENGTHS
   - Each tool may specialize in different CWE categories
   - No single tool detects all vulnerability types comprehensively
""")

# Create a summary visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Individual tool coverage
ax1 = axes[0]
tool_coverage = [len(tool_cwes[tool]) for tool in tools]
ax1.bar(tools, tool_coverage, color=['#3498db', '#e74c3c', '#2ecc71'][:n_tools])
ax1.set_xlabel('Tools', fontsize=12)
ax1.set_ylabel('Number of Unique CWEs', fontsize=12)
ax1.set_title('Individual Tool CWE Coverage', fontsize=14, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

# Plot 2: Pairwise IoU comparison
ax2 = axes[1]
pair_names = []
pair_ious = []
for i in range(n_tools):
    for j in range(i+1, n_tools):
        pair_names.append(f"{tools[i]}\nvs\n{tools[j]}")
        pair_ious.append(iou_matrix[i][j])

ax2.bar(range(len(pair_names)), pair_ious, color=['#9b59b6', '#f39c12', '#1abc9c'][:len(pair_names)])
ax2.set_xlabel('Tool Pairs', fontsize=12)
ax2.set_ylabel('IoU Value', fontsize=12)
ax2.set_title('Pairwise IoU Comparison', fontsize=14, fontweight='bold')
ax2.set_xticks(range(len(pair_names)))
ax2.set_xticklabels(pair_names, fontsize=9)
ax2.set_ylim([0, 1])
ax2.grid(axis='y', alpha=0.3)
ax2.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='IoU = 0.5')
ax2.legend()

plt.tight_layout()
plt.savefig('iou_analysis_summary.png', dpi=300, bbox_inches='tight')
print("\n✓ Summary visualization saved as: iou_analysis_summary.png")
plt.show()

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print(f"\nGenerated files:")
print(f"  1. {output_file} - IoU matrix in CSV format")
print(f"  2. iou_heatmap.png - Heatmap visualization")
print(f"  3. iou_analysis_summary.png - Summary charts")
print("\nUse these results for your lab report!")