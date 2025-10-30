import pandas as pd
import re

def clean_supplier_spend(file_path):
    """
    Cleans and analyzes supplier spend data from a CSV file.

    Args:
        file_path (str): The path to the input CSV file.

    Returns:
        float: The total spend for Zenith Components in the Logistics category.
    """
    # Import the CSV into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Step 1: Trim whitespace on textual columns
    text_cols = ['invoice_id', 'supplier_name', 'category', 'status', 'amount_usd', 'comment']
    for col in text_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()

    # Step 2: Normalize supplier_name
    # A simple normalization: lowercase, remove punctuation and common terms.
    # This is a simplified version of OpenRefine's clustering.
    def normalize_name(name):
        if not isinstance(name, str):
            return name
        name = name.lower()
        name = re.sub(r'[.,-]', '', name)
        name = re.sub(r'\s+(inc|llc|corp|ltd)\b', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name.title() # Convert to title case for consistency

    df['supplier_name_normalized'] = df['supplier_name'].apply(normalize_name)
    
    # Manual mapping for 'Zenith Components' based on likely variations
    # In a real scenario, you would build this map after more analysis
    zenith_variations = ['Zenith Comp', 'Zenith Components']
    df.loc[df['supplier_name_normalized'].isin(zenith_variations), 'supplier_name_normalized'] = 'Zenith Components'


    # Step 3: Remove duplicate invoices by invoice_id, keeping the first entry.
    df.sort_values('invoice_date', inplace=True) # Sort by date to keep the earliest record
    df.drop_duplicates(subset='invoice_id', keep='first', inplace=True)

    # Step 4: Clean amount_usd by stripping currency strings and converting to numbers
    df['amount_usd_cleaned'] = df['amount_usd'].str.replace(r'[^0-9.]', '', regex=True)
    df['amount_usd_cleaned'] = pd.to_numeric(df['amount_usd_cleaned'], errors='coerce')
    df.dropna(subset=['amount_usd_cleaned'], inplace=True) # Drop rows where conversion failed

    # Step 5: Filter rows
    filtered_df = df[
        (df['supplier_name_normalized'] == 'Zenith Components') &
        (df['category'] == 'Logistics') &
        (df['status'] == 'Approved')
    ]

    # Step 6: Compute the total spend in USD
    total_spend = filtered_df['amount_usd_cleaned'].sum()

    print(f"Total spend for Zenith Components in Logistics (Approved): ${total_spend:,.2f}")
    
    return total_spend

if __name__ == '__main__':
    # Assuming the script is in 'Week 6' and the data file is also there.
    csv_file = 'Week 6/q-openrefine-supplier-spend.csv'
    clean_supplier_spend(csv_file)
