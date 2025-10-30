import datetime
import re

count = 0
filename = 'Week 6\\q-shell-log-latency.log'

try:
    with open(filename, 'r') as f:
        for line in f:
            try:
                # Split the line by spaces to get the main components
                parts = line.split(' ')

                # ----------------------------------------------------
                # Check all conditions, skipping if any fail
                # ----------------------------------------------------

                # 1. Filter for GET /download/report
                if not (parts[1] == 'GET' and parts[2].startswith('/download/report')):
                    continue

                # 2. Filter for cluster=aps1
                if not (parts[6] == 'cluster=aps1'):
                    continue

                # 3. Filter for status codes 200-299
                # We use a regex to check for 'status=2xx'
                if not re.match(r'status=2\d{2}', parts[3]):
                    continue

                # 4. Filter for time (Friday, 2:00 - 7:00 UTC)
                timestamp_str = parts[0]  # e.g., '2024-04-17T14:23:11Z'
                
                # Parse the timestamp string into a datetime object
                dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')

                # Check for Friday (weekday() == 4) and hour (2 <= hour < 7)
                if dt.weekday() == 4 and (2 <= dt.hour < 7):
                    # All conditions passed!
                    count += 1
                
            except (IndexError, ValueError) as e:
                # This catches any malformed lines (e.g., blank lines,
                # lines with missing fields, or bad date formats)
                # and safely skips them.
                continue

    # Print the final result
    print(count)

except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")