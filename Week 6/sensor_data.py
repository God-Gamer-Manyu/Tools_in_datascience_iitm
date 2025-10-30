import json  # <-- Changed back to the standard 'json' library
import datetime
import sys

# --- SET TO TRUE TO SEE WHY RECORDS ARE SKIPPED ---
DEBUG = True

def convert_to_celsius(value, unit):
    """Converts a temperature value to Celsius, handling F and K."""
    if unit == "C":
        return value
    elif unit == "F":
        return (value - 32) * 5 / 9
    elif unit == "K":
        return value - 273.15
    else:
        return None

def analyze_sensor_data(filename):
    """
    Streams a JSONL file and computes the average temperature 
    based on the specified criteria.
    """
    
    # --- Define Filters (from your last version) ---
    TARGET_SITE = "Lab-East"
    DEVICE_PREFIX = "pump"
    EXCLUDED_STATUSES = {"maintenance", "offline"}
    
    try:
        START_TIME = datetime.datetime.fromisoformat(
            "2024-08-23 02:56:08.994Z"
        ).replace(tzinfo=datetime.timezone.utc)
        
        END_TIME = datetime.datetime.fromisoformat(
            "2024-08-31 23:59:59Z"
        ).replace(tzinfo=datetime.timezone.utc)
        
    except ValueError as e:
        print(f"Error: Invalid timestamp format in script: {e}", file=sys.stderr)
        return

    # --- Initialize Aggregators ---
    total_celsius = 0.0
    record_count = 0

    # --- Stream and Process File ---
    try:
        # --- THIS BLOCK IS NOW FIXED ---
        # Open in 'r' (text) mode for the standard json library
        with open(filename, 'r') as f:
            
            # This is the correct way to stream a JSONL file.
            # It reads one line at a time into memory.
            for line_number, line in enumerate(f, 1):
                try:
                    # Skip empty lines
                    if not line.strip():
                        continue

                    # 1. Parse the single line of JSON
                    data = json.loads(line)
                    
                    # --- DEBUG: Print the raw object if flag is on ---
                    if DEBUG and line_number < 20: 
                        print(f"\n--- [DEBUG] Processing line {line_number}: {data}")

                    # 2. Filter by Site
                    site = data.get("site")
                    if site != TARGET_SITE:
                        if DEBUG: print(f"[DEBUG] Skip: Site is '{site}', not '{TARGET_SITE}'")
                        continue
                        
                    # 3. Filter by Device Prefix
                    device = data.get("device", "")
                    if not device.startswith(DEVICE_PREFIX):
                        if DEBUG: print(f"[DEBUG] Skip: Device '{device}' doesn't start with '{DEVICE_PREFIX}'")
                        continue
                        
                    # 4. Filter by Status
                    status = data.get("status")
                    if status in EXCLUDED_STATUSES:
                        if DEBUG: print(f"[DEBUG] Skip: Status is '{status}'")
                        continue

                    # 5. Filter by Time Window
                    timestamp_str = data.get("captured_at")
                    if not timestamp_str:
                        if DEBUG: print(f"[DEBUG] Skip: Missing 'captured_at'")
                        continue
                        
                    current_time = datetime.datetime.fromisoformat(
                        timestamp_str
                    ).replace(tzinfo=datetime.timezone.utc)
                    
                    if not (START_TIME <= current_time <= END_TIME):
                        if DEBUG: print(f"[DEBUG] Skip: Timestamp '{timestamp_str}' is outside window")
                        continue

                    # 6. Extract and convert temperature
                    temp_data = data.get("metrics", {}).get("temperature")
                    if not temp_data or "value" not in temp_data or "unit" not in temp_data:
                        if DEBUG: print(f"[DEBUG] Skip: Missing temperature data")
                        continue
                        
                    value = temp_data["value"]
                    unit = temp_data["unit"]
                    celsius = convert_to_celsius(value, unit)
                    
                    # 7. Add to totals
                    if celsius is not None:
                        if DEBUG: print(f"[DEBUG] SUCCESS: Adding {celsius:.2f}C from record {line_number}")
                        total_celsius += celsius
                        record_count += 1
                    else:
                        if DEBUG: print(f"[DEBUG] Skip: Invalid temperature unit '{unit}'")

                except json.JSONError as e: # type: ignore
                    # Catches errors from malformed JSON on a specific line
                    print(f"Skipping malformed JSON in line {line_number}: {e}", file=sys.stderr)
                except (TypeError, KeyError) as e:
                    # Catches errors in data processing (e.g., missing keys)
                    print(f"Skipping malformed data in record {line_number}: {e}", file=sys.stderr)
                except ValueError as e:
                    # Catches errors from datetime.fromisoformat or float conversion
                    print(f"Skipping record {line_number} with bad data: {e}", file=sys.stderr)

        # --- Calculate and Report Final Average ---
        print("\n--- FINAL RESULT ---")
        if record_count > 0:
            average_temp = total_celsius / record_count
            print(f"{average_temp:.2f}")
        else:
            print("No matching records found.")
            
    except FileNotFoundError:
        print(f"Error: File not found at '{filename}'", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# --- Run the Analysis ---
if __name__ == "__main__":
    FILENAME = "Week 6/q-json-sensor-rollup.jsonl"
    analyze_sensor_data(FILENAME)

