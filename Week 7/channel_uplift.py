import pandas as pd
import os

CSV_PATH = r"d:\Rtamanyu\_IIt Madras\2nd year\sem 1\Tools in datascience\Week 7\q-python-channel-conversion.csv"


def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found at {path}")
    return pd.read_csv(path)


def compute_uplift(df):
    # Aggregate totals by channel and segment
    agg = df.groupby(['channel', 'segment']).agg({'sessions': 'sum', 'conversions': 'sum'}).reset_index()
    agg['conversion_rate'] = agg.apply(lambda r: (r['conversions'] / r['sessions']) if r['sessions'] > 0 else 0.0, axis=1)

    # Pivot conversion rates so columns are segments
    pivot = agg.pivot(index='channel', columns='segment', values='conversion_rate')

    # Ensure both columns present
    for seg in ['Premium', 'Standard']:
        if seg not in pivot.columns:
            pivot[seg] = 0.0

    # Compute uplift: Premium - Standard
    pivot['uplift'] = pivot['Premium'] - pivot['Standard']

    # Convert to decimals; already decimal (e.g., 0.03). We'll also prepare percentage
    pivot = pivot.sort_values('uplift', ascending=False)
    return agg, pivot


if __name__ == '__main__':
    df = load_data(CSV_PATH)
    agg, pivot = compute_uplift(df)

    pd.set_option('display.float_format', lambda x: f"{x:.6f}")
    print("Aggregated totals by channel and segment (sessions, conversions, conversion_rate):")
    print(agg)
    print("\nConversion rate pivot (rows=channel, cols=segments) with uplift (Premium - Standard):")
    print(pivot[['Premium','Standard','uplift']])

    # Channel with largest positive uplift
    top = pivot['uplift'].idxmax()
    top_uplift = pivot.loc[top, 'uplift']

    print(f"\nChannel with largest Premium uplift over Standard: {top}")
    print(f"Uplift (decimal): {top_uplift:.6f}")
    print(f"Uplift (percentage points): {top_uplift*100:.2f}%")
