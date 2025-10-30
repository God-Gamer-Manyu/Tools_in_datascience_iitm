
import pandas as pd
import re

# --- Data Analysis ---

REGIONS = [
    {"canonical": "North America", "variants": ["NorthAmerica", "N. America", "N America", "North-Am"]},
    {"canonical": "Latin America", "variants": ["LatAm", "Latin-America", "LAT AM", "LatinAmerica"]},
    {"canonical": "Europe", "variants": ["EU", "Europa", "Europe Region", "E.U."]},
    {"canonical": "Middle East & Africa", "variants": ["MEA", "MiddleEast&Africa", "M. East Africa", "Middle East/Africa"]},
    {"canonical": "Asia Pacific", "variants": ["APAC", "Asia-Pacific", "AsiaPac", "Asia Pacific Region"]}
]

def parse_money(value):
    """Parses a string like '$1,234.56 USD' into a float."""
    if not isinstance(value, str):
        return None
    try:
        return float(re.sub(r'[^\d.]', '', value))
    except (ValueError, TypeError):
        return None

def get_canonical_region(value):
    """Finds the canonical region name from a variant."""
    if not isinstance(value, str):
        return None
    val_norm = value.strip().lower()
    for region in REGIONS:
        if val_norm == region["canonical"].lower():
            return region["canonical"]
        for variant in region["variants"]:
            if val_norm == variant.lower():
                return region["canonical"]
    return None

def solve_from_excel(file_path):
    """
    Reads the generated excel file and computes the consolidated margin.
    """
    df = pd.read_excel(file_path)

    # Clean up column names (remove leading/trailing spaces)
    df.columns = df.columns.str.strip()

    # Normalize data
    df['Revenue'] = df['Revenue (reported)'].apply(parse_money)
    df['Expense'] = df['Expense (reported)'].apply(parse_money)
    df['Canonical Region'] = df['Region'].apply(get_canonical_region)
    
    # Extract Category from 'Ops Notes'
    df['Category'] = df['Ops Notes'].str.strip().str.split('|').str[0]

    # The cutoff date from index.html is June 6, 2024.
    # We need to parse the 'Closing Period' column. This is tricky because of multiple formats.
    # For this specific problem, we know the raw data is generated with a date.
    # A robust solution would handle all formats. A simpler one for now:
    # We can filter by year and quarter/month from the 'Ops Notes' as a proxy.
    # Format is YYYY-QQ
    df['Year'] = df['Ops Notes'].str.strip().str.split('|').str[2].str.split('-').str[0].astype(int)
    df['Quarter'] = df['Ops Notes'].str.strip().str.split('|').str[2].str.split('-').str[1].astype(int)

    # Filter for Asia Pacific, Billing, and before or on June 6, 2024
    # June 6, 2024 is in Q2 2024. So we include 2023 and Q1, Q2 of 2024.
    target_region = "Asia Pacific"
    target_category = "Billing"

    # Try to parse an exact closing date if available; otherwise approximate with quarter-end.
    if 'Closing Period' in df.columns:
        df['Closing Date'] = pd.to_datetime(df['Closing Period'], errors='coerce')
    else:
        q_end_month = {1: 3, 2: 6, 3: 9, 4: 12}
        df['Closing Date'] = pd.to_datetime(
            df['Year'].astype(str) + '-' + df['Quarter'].map(q_end_month).astype(str) + '-01',
            errors='coerce'
        ) + pd.offsets.MonthEnd(0)

    # Cutoff is on or before 2024-06-06
    cutoff = pd.Timestamp('2024-06-06')

    # Exclude any 2024 rows whose actual/approximated closing date is after the cutoff.
    # Also conservatively exclude 2024 rows with unknown closing date.
    mask_exclude = (df['Year'] == 2024) & (
        df['Closing Date'].isna() | (df['Closing Date'] > cutoff)
    )
    # Set Quarter to a value >2 so the existing Year/Quarter filter will exclude them.
    df.loc[mask_exclude, 'Quarter'] = 3
    
    filtered_df = df[
        (df['Canonical Region'] == target_region) &
        (df['Category'] == target_category) &
        ((df['Year'] < 2024) | ((df['Year'] == 2024) & (df['Quarter'] <= 2)))
    ].copy()

    # Impute expense where it's null
    margin_rate = 0.37
    filtered_df['Expense_imputed'] = filtered_df.apply(
        lambda row: row['Expense'] if pd.notna(row['Expense']) else row['Revenue'] * margin_rate,
        axis=1
    )

    # Calculate profit
    filtered_df['Profit'] = filtered_df['Revenue'] - filtered_df['Expense_imputed']
    
    # Sum up the profit
    total_profit = filtered_df['Profit'].sum()

    return total_profit

if __name__ == "__main__":
    # Assume the data is already stored in the folder as .xlsx
    excel_file = "Week 6/q-excel-operational-metrics_raw.xlsx"
    
    # Solve the problem using the generated Excel file
    consolidated_margin = solve_from_excel(excel_file)
    
    print("\n--- Calculation Result ---")
    print(f"The consolidated margin is: ${consolidated_margin:,.2f}")

