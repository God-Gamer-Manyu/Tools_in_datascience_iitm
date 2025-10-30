import datetime
import re
import sys

total_failed_bytes = 0
filename = 'Week 6\\q-shell-log-download-errors.log'

# We use a regex to safely parse the log format.
# This avoids errors with spaces in user agents.
# Groups: 1=Timestamp, 2=Method, 3=Path, 4=Status, 5=Bytes, 6=Cluster, 7=Referer
log_pattern = re.compile(
    r'^(\S+) (\S+) (\S+) status=(\d+) bytes=(\d+) rt=\S+ cluster=(\S+) referer="([^"]+)"'
)

try:
    with open(filename, 'r') as f:
        for line in f:
            # 1. Parse the line using regex
            match = log_pattern.match(line)
            if not match:
                continue  # Skip any line that doesn't match our format

            # 2. Extract matched groups
            timestamp_str, method, path, status_str, bytes_str, cluster, referer = match.groups()

            # 3. Apply all filters. We check the simplest/fastest ones first.
            
            # Filter for GET
            if method != 'GET':
                continue

            # Filter for cluster=aps1
            if cluster != 'aps1':
                continue

            # Filter for referer
            if referer != 'https://finance.orbit.example.com':
                continue
                
            # Filter for path
            if not path.startswith('/download/report'):
                continue

            # Filter for 4xx client errors
            try:
                status = int(status_str)
                if not (400 <= status <= 499):
                    continue
            except ValueError:
                continue # Bad status number

            # Filter for weekend traffic (Saturday=5, Sunday=6)
            try:
                dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
                if dt.weekday() not in [5, 6]:
                    continue
            except ValueError:
                continue # Bad timestamp

            # 4. If all conditions passed, sum the bytes
            try:
                total_failed_bytes += int(bytes_str)
            except ValueError:
                continue # Bad bytes number

    # 5. Report the final total
    print(total_failed_bytes)

except FileNotFoundError:
    print(f"Error: File '{filename}' not found.", file=sys.stderr)
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)