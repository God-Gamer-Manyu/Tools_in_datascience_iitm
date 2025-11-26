import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Try to import seaborn, but fall back to matplotlib if unavailable
try:
    import seaborn as sns
    _HAS_SEABORN = True
except Exception:
    sns = None
    _HAS_SEABORN = False

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

# Create heatmap PNG (ensure output is smaller than 512x512 pixels)
png_path = os.path.join(here, 'heatmap.png')
# Create red-white-green colormap
cmap = LinearSegmentedColormap.from_list('red_white_green', ['#b2182b', '#ffffff', '#1a9629'])

# Target pixel size (max 512). We'll use 500x500 to be safely under 512.
pixel_size = 500
dpi = 100
figsize_inches = (pixel_size / dpi, pixel_size / dpi)

plt.figure(figsize=figsize_inches)
if _HAS_SEABORN:
    sns.set(style='white')
    ax = sns.heatmap(corr, annot=True, fmt='.2f', cmap=cmap, vmin=-1, vmax=1, square=True,
                     cbar_kws={'shrink': 0.8}, linewidths=0.5, linecolor='gray')
else:
    # Fallback: use matplotlib imshow and annotate values
    ax = plt.gca()
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    # Annotations
    for (i, j), val in np.ndenumerate(corr.values):
        ax.text(j, i, f"{val:.2f}", ha='center', va='center', color='black', fontsize=8)
    # Tick labels
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.index)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr.index)
    plt.colorbar(im, fraction=0.046, pad=0.04)

plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig(png_path, dpi=dpi)
plt.close()
print('Saved heatmap PNG to', png_path, '(size <= {}x{} pixels)'.format(pixel_size, pixel_size))

print('Done')
