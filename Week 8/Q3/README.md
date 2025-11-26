Correlation analysis for supply chain metrics

Files in this folder:

- `q-excel-correlation-heatmap.xlsx` — source Excel file (provided)
- `generate_correlation.py` — script used to compute correlation and create heatmap
- `correlation.csv` — generated correlation matrix (CSV)
- `heatmap.png` — generated heatmap screenshot (Excel-style red-white-green palette)

Contact: 24f3001383@ds.study.iitm.ac.in

How this was generated:
1. The provided Excel file was read with `pandas`.
2. A correlation matrix for the five supply-chain metrics was computed with `DataFrame.corr()`.
3. The matrix was exported as `correlation.csv`.
4. A heatmap (red-white-green) was plotted with `seaborn` and saved as `heatmap.png`.

To reproduce locally (Windows cmd):

```
python -m pip install --upgrade pip
python -m pip install pandas openpyxl matplotlib seaborn pillow
python "Week 8\Q3\generate_correlation.py"
```

If the script cannot auto-detect the expected column names, it will fall back to the first five numeric columns.
