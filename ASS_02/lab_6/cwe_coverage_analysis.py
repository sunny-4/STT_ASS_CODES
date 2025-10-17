import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# CWE Top 25 for 2024
CWE_TOP_25 = [
    'CWE-79', 'CWE-787', 'CWE-89', 'CWE-416', 'CWE-78', 'CWE-20', 'CWE-125',
    'CWE-22', 'CWE-352', 'CWE-434', 'CWE-862', 'CWE-476', 'CWE-287', 'CWE-190',
    'CWE-502', 'CWE-77', 'CWE-119', 'CWE-798', 'CWE-918', 'CWE-306', 'CWE-362',
    'CWE-269', 'CWE-94', 'CWE-863', 'CWE-276'
]

# Read the consolidated CSV
print("=" * 80)
print("CWE COVERAGE ANALYSIS")
print("=" * 80)

df = pd.read_csv('consolidated_cwe_findings.csv')

print(f"\n📊 Dataset Overview:")
print(f"  Total entries: {len(df)}")
print(f"  Unique CWEs: {df['CWE_ID'].nunique()}")
print(f"  Tools analyzed: {df['Tool_name'].nunique()}")
print(f"  Projects analyzed: {df['Project_name'].nunique()}")

# ============================================================================
# 1. EXTRACT UNIQUE CWE IDs PER TOOL
# ============================================================================
print("\n" + "=" * 80)
print("1. UNIQUE CWE IDs DETECTED BY EACH TOOL")
print("=" * 80)

tool_cwes = {}
for tool in df['Tool_name'].unique():
    tool_data = df[df['Tool_name'] == tool]
    unique_cwes = set(tool_data['CWE_ID'].unique())
    tool_cwes[tool] = unique_cwes
    print(f"\n{tool}:")
    print(f"  Unique CWEs detected: {len(unique_cwes)}")
    print(f"  CWE IDs: {sorted(unique_cwes)}")

# ============================================================================
# 2. COMPUTE TOP 25 CWE COVERAGE
# ============================================================================
print("\n" + "=" * 80)
print("2. TOP 25 CWE COVERAGE PER TOOL")
print("=" * 80)

coverage_data = []
for tool, cwes in tool_cwes.items():
    top25_detected = cwes.intersection(set(CWE_TOP_25))
    coverage_pct = (len(top25_detected) / len(CWE_TOP_25)) * 100
    
    coverage_data.append({
        'Tool': tool,
        'Total_Unique_CWEs': len(cwes),
        'Top25_Detected': len(top25_detected),
        'Top25_Coverage_Pct': coverage_pct,
        'Top25_CWEs': sorted(top25_detected)
    })
    
    print(f"\n{tool}:")
    print(f"  Total unique CWEs: {len(cwes)}")
    print(f"  Top 25 CWEs detected: {len(top25_detected)}/25")
    print(f"  Coverage: {coverage_pct:.1f}%")
    print(f"  Detected Top 25: {sorted(top25_detected)}")

coverage_df = pd.DataFrame(coverage_data)

# ============================================================================
# 3. VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("3. GENERATING VISUALIZATIONS")
print("=" * 80)

# Create a figure with multiple subplots
fig = plt.figure(figsize=(16, 12))

# --- Plot 1: Top 25 Coverage by Tool (Bar Chart) ---
ax1 = plt.subplot(2, 3, 1)
bars = ax1.bar(coverage_df['Tool'], coverage_df['Top25_Coverage_Pct'], 
               color=['#3498db', '#e74c3c', '#2ecc71'])
ax1.set_xlabel('Tool', fontsize=12, fontweight='bold')
ax1.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold')
ax1.set_title('Top 25 CWE Coverage by Tool', fontsize=14, fontweight='bold')
ax1.set_ylim(0, 100)
ax1.grid(axis='y', alpha=0.3)

# Add percentage labels on bars
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}%',
             ha='center', va='bottom', fontweight='bold')

# --- Plot 2: Total Unique CWEs by Tool (Bar Chart) ---
ax2 = plt.subplot(2, 3, 2)
bars2 = ax2.bar(coverage_df['Tool'], coverage_df['Total_Unique_CWEs'],
                color=['#9b59b6', '#f39c12', '#1abc9c'])
ax2.set_xlabel('Tool', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Unique CWEs', fontsize=12, fontweight='bold')
ax2.set_title('Total Unique CWEs Detected by Tool', fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}',
             ha='center', va='bottom', fontweight='bold')

# --- Plot 3: Top 25 vs Other CWEs (Stacked Bar) ---
ax3 = plt.subplot(2, 3, 3)
top25_counts = coverage_df['Top25_Detected']
other_counts = coverage_df['Total_Unique_CWEs'] - coverage_df['Top25_Detected']

x_pos = range(len(coverage_df['Tool']))
ax3.bar(x_pos, top25_counts, label='Top 25 CWEs', color='#e74c3c')
ax3.bar(x_pos, other_counts, bottom=top25_counts, label='Other CWEs', color='#95a5a6')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(coverage_df['Tool'])
ax3.set_xlabel('Tool', fontsize=12, fontweight='bold')
ax3.set_ylabel('Number of CWEs', fontsize=12, fontweight='bold')
ax3.set_title('CWE Distribution: Top 25 vs Others', fontsize=14, fontweight='bold')
ax3.legend()
ax3.grid(axis='y', alpha=0.3)

# --- Plot 4: Total Findings by Tool ---
ax4 = plt.subplot(2, 3, 4)
findings_by_tool = df.groupby('Tool_name')['Number_of_Findings'].sum()
bars4 = ax4.bar(findings_by_tool.index, findings_by_tool.values,
                color=['#34495e', '#e67e22', '#16a085'])
ax4.set_xlabel('Tool', fontsize=12, fontweight='bold')
ax4.set_ylabel('Total Findings', fontsize=12, fontweight='bold')
ax4.set_title('Total Vulnerability Findings by Tool', fontsize=14, fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

for bar in bars4:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height):,}',
             ha='center', va='bottom', fontweight='bold', fontsize=9)

# --- Plot 5: CWE Detection Heatmap ---
ax5 = plt.subplot(2, 3, 5)
# Create a matrix of tool vs top 25 CWEs
tools = df['Tool_name'].unique()
heatmap_data = []
for tool in tools:
    tool_data = df[df['Tool_name'] == tool]
    row = []
    for cwe in CWE_TOP_25[:10]:  # Show first 10 for readability
        if cwe in tool_data['CWE_ID'].values:
            row.append(1)
        else:
            row.append(0)
    heatmap_data.append(row)

sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='RdYlGn',
            xticklabels=CWE_TOP_25[:10], yticklabels=tools,
            cbar_kws={'label': 'Detected (1=Yes, 0=No)'},
            ax=ax5)
ax5.set_title('Top 10 CWE Detection Matrix', fontsize=14, fontweight='bold')
ax5.set_xlabel('CWE ID', fontsize=12, fontweight='bold')
ax5.set_ylabel('Tool', fontsize=12, fontweight='bold')

# --- Plot 6: Findings Distribution by Project and Tool ---
ax6 = plt.subplot(2, 3, 6)
pivot_data = df.pivot_table(values='Number_of_Findings', 
                             index='Project_name', 
                             columns='Tool_name', 
                             aggfunc='sum',
                             fill_value=0)
pivot_data.plot(kind='bar', ax=ax6, width=0.8)
ax6.set_xlabel('Project', fontsize=12, fontweight='bold')
ax6.set_ylabel('Number of Findings', fontsize=12, fontweight='bold')
ax6.set_title('Findings by Project and Tool', fontsize=14, fontweight='bold')
ax6.legend(title='Tool', fontsize=9)
ax6.grid(axis='y', alpha=0.3)
plt.setp(ax6.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('cwe_coverage_analysis.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: cwe_coverage_analysis.png")

# ============================================================================
# 4. ADDITIONAL ANALYSIS PLOTS
# ============================================================================

# Plot: Venn Diagram-style analysis (CWE overlap)
fig2, axes = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: Top 25 CWE Coverage Comparison
ax_left = axes[0]
coverage_comparison = coverage_df[['Tool', 'Top25_Detected', 'Top25_Coverage_Pct']]
colors = ['#3498db', '#e74c3c', '#2ecc71']
bars = ax_left.barh(coverage_comparison['Tool'], coverage_comparison['Top25_Detected'], 
                     color=colors)
ax_left.set_xlabel('Number of Top 25 CWEs Detected', fontsize=12, fontweight='bold')
ax_left.set_ylabel('Tool', fontsize=12, fontweight='bold')
ax_left.set_title('Top 25 CWE Detection Comparison', fontsize=14, fontweight='bold')
ax_left.set_xlim(0, 25)
ax_left.axvline(x=25, color='red', linestyle='--', linewidth=2, label='Maximum (25)')
ax_left.legend()
ax_left.grid(axis='x', alpha=0.3)

# Add count and percentage labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    pct = coverage_comparison.iloc[i]['Top25_Coverage_Pct']
    ax_left.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
                 f'{int(width)} ({pct:.1f}%)',
                 ha='left', va='center', fontweight='bold')

# Plot 2: Tool Effectiveness Score
ax_right = axes[1]
# Calculate effectiveness: (Top25_Coverage * 0.6) + (Total_Unique_CWEs/max * 0.4)
max_cwes = coverage_df['Total_Unique_CWEs'].max()
effectiveness = (coverage_df['Top25_Coverage_Pct'] * 0.6) + \
                ((coverage_df['Total_Unique_CWEs'] / max_cwes) * 100 * 0.4)

bars2 = ax_right.barh(coverage_df['Tool'], effectiveness, color=colors)
ax_right.set_xlabel('Effectiveness Score', fontsize=12, fontweight='bold')
ax_right.set_ylabel('Tool', fontsize=12, fontweight='bold')
ax_right.set_title('Tool Effectiveness Score\n(60% Top25 Coverage + 40% CWE Breadth)', 
                   fontsize=14, fontweight='bold')
ax_right.set_xlim(0, 100)
ax_right.grid(axis='x', alpha=0.3)

for bar in bars2:
    width = bar.get_width()
    ax_right.text(width + 1, bar.get_y() + bar.get_height()/2.,
                  f'{width:.1f}',
                  ha='left', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('cwe_coverage_comparison.png', dpi=300, bbox_inches='tight')
print("  ✓ Saved: cwe_coverage_comparison.png")

# ============================================================================
# 5. DETAILED COVERAGE TABLE
# ============================================================================
print("\n" + "=" * 80)
print("4. DETAILED COVERAGE TABLE")
print("=" * 80)

# Save detailed coverage table
coverage_table = coverage_df[['Tool', 'Total_Unique_CWEs', 'Top25_Detected', 'Top25_Coverage_Pct']]
coverage_table.to_csv('tool_cwe_coverage_summary.csv', index=False)
print("\n✓ Saved: tool_cwe_coverage_summary.csv")

print("\nCoverage Summary Table:")
print(coverage_table.to_string(index=False))

# ============================================================================
# 6. CWE OVERLAP ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("5. CWE OVERLAP BETWEEN TOOLS")
print("=" * 80)

tools_list = list(tool_cwes.keys())
for i in range(len(tools_list)):
    for j in range(i + 1, len(tools_list)):
        tool1 = tools_list[i]
        tool2 = tools_list[j]
        
        cwes1 = tool_cwes[tool1]
        cwes2 = tool_cwes[tool2]
        
        intersection = cwes1.intersection(cwes2)
        union = cwes1.union(cwes2)
        
        print(f"\n{tool1} ∩ {tool2}:")
        print(f"  Common CWEs: {len(intersection)}")
        print(f"  CWEs: {sorted(intersection)}")
        print(f"  {tool1} only: {len(cwes1 - cwes2)} CWEs")
        print(f"  {tool2} only: {len(cwes2 - cwes1)} CWEs")

print("\n" + "=" * 80)
print("✓ ANALYSIS COMPLETE!")
print("=" * 80)
print("\nGenerated files:")
print("  1. cwe_coverage_analysis.png - Comprehensive coverage visualizations")
print("  2. cwe_coverage_comparison.png - Tool comparison charts")
print("  3. tool_cwe_coverage_summary.csv - Detailed coverage data")
print("\nUse these visualizations in your lab report!")