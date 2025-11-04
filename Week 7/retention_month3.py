import pandas as pd
import os

# Absolute path to CSV (provided in workspace attachments)
CSV_PATH = r"d:\Rtamanyu\_IIt Madras\2nd year\sem 1\Tools in datascience\Week 7\q-python-cohort-retention.csv"
COHORT = '2024-01'
TARGET_MONTH = 3  # month_offset for Month 3


def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found at {path}")
    return pd.read_csv(path)


def compute_retention(df, cohort_month, month=3):
    # Ensure correct dtypes
    df = df.copy()
    df['signup_month'] = df['signup_month'].astype(str)
    df['month_offset'] = pd.to_numeric(df['month_offset'], errors='coerce').fillna(-1).astype(int)
    df['active_flag'] = pd.to_numeric(df['active_flag'], errors='coerce').fillna(0).astype(int)

    # cohort size: unique customers in signup_month at month_offset == 0
    cohort0 = df[(df['signup_month'] == cohort_month) & (df['month_offset'] == 0)]
    cohort_size = cohort0['customer_id'].nunique()

    if cohort_size == 0:
        return None, cohort_size

    # active customers in target month for the same signup cohort
    active_m = df[(df['signup_month'] == cohort_month) & (df['month_offset'] == month) & (df['active_flag'] == 1)]
    active_count = active_m['customer_id'].nunique()

    retention = active_count / cohort_size
    return retention, (cohort_size, active_count)


def build_retention_pivot(df):
    # Count unique customers with active_flag==1 per cohort and month_offset
    active = df[df['active_flag'] == 1]
    pivot_counts = active.pivot_table(index='signup_month', columns='month_offset', values='customer_id', aggfunc=lambda x: x.nunique(), fill_value=0)

    # cohort sizes (month 0 unique customers)
    cohort_sizes = df[df['month_offset'] == 0].groupby('signup_month')['customer_id'].nunique()

    # Convert counts to retention rates by dividing by cohort size
    retention_rates = pivot_counts.div(cohort_sizes, axis=0).fillna(0)
    return pivot_counts.sort_index(), retention_rates.sort_index()


if __name__ == '__main__':
    df = load_data(CSV_PATH)

    pivot_counts, retention_rates = build_retention_pivot(df)

    print("Unique active customers (counts) pivot:\n", pivot_counts)
    print("\nRetention rates pivot (rows=signup_month, cols=month_offset):\n", retention_rates)

    retention, meta = compute_retention(df, COHORT, TARGET_MONTH)
    if retention is None:
        print(f"\nCohort {COHORT} not found or cohort size is zero. cohort_size={meta}")
    else:
        cohort_size, active_count = meta
        print(f"\nCohort {COHORT} - cohort size (month 0 unique customers): {cohort_size}")
        print(f"Active customers in month {TARGET_MONTH}: {active_count}")
        print(f"Month {TARGET_MONTH} retention for cohort {COHORT}: {retention:.4f} ({retention*100:.1f}%)")
