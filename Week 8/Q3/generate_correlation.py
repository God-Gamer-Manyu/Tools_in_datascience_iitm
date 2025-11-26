import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

here = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(here, 'q-excel-correlation-heatmap.xlsx')
if not os.path.exists(excel_path):
    print('ERROR: Excel file not found at', excel_path)
    sys.exit(2)

print('Reading Excel file:', excel_path)
# Read the first sheet
try:
    df = pd.read_excel(excel_path)
except Exception as e:
    print('Failed to read Excel file:', e)
    sys.exit(3)

print('Columns found:', list(df.columns))
# Expected columns
expected = ['Supplier_Lead_Time','Inventory_Levels','Order_Frequency','Delivery_Performance','Cost_Per_Unit']

# Helper to match column names ignoring case/whitespace/punctuation
def normalize(s):
    return ''.join(ch.lower() for ch in str(s) if ch.isalnum())

col_map = {}
for e in expected:
    ne = normalize(e)
    for c in df.columns:
        if normalize(c) == ne:
            col_map[e] = c
            break

# If any expected not found, try partial match
for e in expected:
    if e in col_map:
        continue
    ne = normalize(e)
    for c in df.columns:
        if ne in normalize(c) or normalize(c) in ne:
            col_map[e] = c
            break

print('Mapped columns:', col_map)
# If still missing, fallback to numeric columns (take first 5 numeric)
selected_cols = []
for e in expected:
    if e in col_map:
        selected_cols.append(col_map[e])

if len(selected_cols) < len(expected):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print('Numeric columns available:', numeric_cols)
    # take first 5 numeric
    selected_cols = numeric_cols[:5]
    if len(selected_cols) < 2:
        print('Not enough numeric columns to compute correlation. Exiting.')
        sys.exit(4)

print('Selected columns for correlation:', selected_cols)
sub = df[selected_cols].copy()
# Drop rows with all NaNs in these columns
sub = sub.dropna(how='all')
# If any non-numeric, coerce
for c in sub.columns:
    if not pd.api.types.is_numeric_dtype(sub[c]):
        sub[c] = pd.to_numeric(sub[c], errors='coerce')

corr = sub.corr()
print('Correlation matrix:\n', corr)

# Save CSV
csv_path = os.path.join(here, 'correlation.csv')
corr.to_csv(csv_path, index=True)
print('Saved correlation CSV to', csv_path)

# Create heatmap PNG
png_path = os.path.join(here, 'heatmap.png')
# Create red-white-green colormap
cmap = LinearSegmentedColormap.from_list('red_white_green', ['#b2182b','#f7f7f7','#2166ac'])
plt.figure(figsize=(6,6))
sns.set(style='white')
ax = sns.heatmap(corr, annot=True, fmt='.2f', cmap=cmap, vmin=-1, vmax=1, square=True, cbar_kws={'shrink':0.8}, linewidths=0.5, linecolor='gray')
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig(png_path, dpi=96)  # 6in * 96 dpi = 576 px -> will be around 576x576
plt.close()
print('Saved heatmap PNG to', png_path)

print('Done')
