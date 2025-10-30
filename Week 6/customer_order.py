import json
import datetime
import sys

def analyze_customer_data(filename):
    """
    Streams a JSONL file of customer data and computes the total quantity
    of items sold based on a specific set of filters.
    """
    
    # --- Define Filters ---
    TARGET_REGION = "Asia Pacific"
    TARGET_CHANNEL = "App"
    TARGET_CATEGORY = "Infrastructure"
    
    try:
        # Define the date range (inclusive)
        START_DATE = datetime.date(2024, 8, 23)
        END_DATE = datetime.date(2024, 9, 13)
    except ValueError as e:
        print(f"Error: Invalid date format in script: {e}", file=sys.stderr)
        return

    # --- Initialize Aggregator ---
    total_quantity = 0

    # --- Stream and Process File ---
    try:
        with open(filename, 'r') as f:
            
            # Read the file line by line (this is the streaming part)
            for line_number, line in enumerate(f, 1):
                try:
                    # Skip empty lines
                    if not line.strip():
                        continue

                    # 1. Parse the single line of JSON
                    data = json.loads(line)

                    # 2. Filter by Region
                    if data.get("region") != TARGET_REGION:
                        continue
                        
                    # 3. Explode the "orders" array
                    for order in data.get("orders", []):
                        
                        # 4. Filter by Channel
                        if order.get("channel") != TARGET_CHANNEL:
                            continue
                            
                        # 5. Filter by Order Date
                        order_date_str = order.get("order_date")
                        if not order_date_str:
                            continue
                            
                        # Parse the ISO date string (e.g., "2024-08-18T10:11:06.445Z")
                        # and convert it to a simple date object for comparison.
                        order_date = datetime.datetime.fromisoformat(
                            order_date_str.replace("Z", "+00:00")
                        ).date()
                        
                        if not (START_DATE <= order_date <= END_DATE):
                            continue
                            
                        # 6. Explode the "items" array
                        for item in order.get("items", []):
                            
                            # 7. Filter by Category
                            if item.get("category") != TARGET_CATEGORY:
                                continue
                                
                            # 8. All filters passed! Sum the quantity.
                            # Use .get("quantity", 0) to handle missing keys safely
                            total_quantity += item.get("quantity", 0)

                except json.JSONError as e:#type: ignore
                    # Catches errors from malformed JSON on a specific line
                    print(f"Skipping malformed JSON in line {line_number}: {e}", file=sys.stderr)
                except (TypeError, KeyError) as e:
                    # Catches errors in data processing (e.g., missing keys)
                    print(f"Skipping malformed data in record {line_number}: {e}", file=sys.stderr)
                except ValueError as e:
                    # Catches errors from datetime.fromisoformat
                    print(f"Skipping record {line_number} with bad data: {e}", file=sys.stderr)

        # --- Report Final Total ---
        print(total_quantity)
            
    except FileNotFoundError:
        print(f"Error: File not found at '{filename}'", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# --- Run the Analysis ---
if __name__ == "__main__":
    FILENAME = "Week 6/q-json-customer-flatten.jsonl"
    analyze_customer_data(FILENAME)
