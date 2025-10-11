import requests
import json

# The endpoint URL from your deployment
url = "https://iitmverceltest-cnqq18vhr-rtamanyu-n-js-projects.vercel.app/api/index"

# Test data as per grader
payload = {
    "regions": ["emea", "apac"],
    "threshold_ms": 165
}

headers = {
    "Content-Type": "application/json"
}

# Step 1: Test OPTIONS for CORS preflight
options_response = requests.options(url, headers=headers)
print("OPTIONS Response Status:", options_response.status_code)
print("CORS Header (Access-Control-Allow-Origin):", options_response.headers.get("Access-Control-Allow-Origin", "MISSING"))
if options_response.status_code == 200 and options_response.headers.get("Access-Control-Allow-Origin") == "*":
    print("✅ CORS preflight passed")
else:
    print("❌ CORS preflight failed")

# Step 2: Send POST request
response = requests.post(url, data=json.dumps(payload), headers=headers)

print("\nPOST Response Status:", response.status_code)
print("CORS Header (Access-Control-Allow-Origin):", response.headers.get("Access-Control-Allow-Origin", "MISSING"))
if response.status_code == 200 and response.headers.get("Access-Control-Allow-Origin") == "*":
    print("✅ CORS on POST passed")
else:
    print("❌ CORS on POST failed")

# Step 3: Parse and check response body
if response.status_code == 200:
    try:
        result = response.json()
        print("\nResponse Body:")
        print(json.dumps(result, indent=2))
        
        # Expected metrics (computed from data)
        expected = {
            "emea": {
                "avg_latency": 151.69,
                "p95_latency": 196.96,
                "avg_uptime": 98.43,
                "breaches": 4
            },
            "apac": {
                "avg_latency": 167.09,
                "p95_latency": 210.05,
                "avg_uptime": 98.24,
                "breaches": 7
            }
        }
        
        # Check if matches (allowing for minor float differences)
        match = True
        for region, metrics in expected.items():
            if region in result:
                for key, exp_val in metrics.items():
                    act_val = result[region][key]
                    if isinstance(exp_val, float) and abs(act_val - exp_val) > 0.01:
                        match = False
                        print(f"❌ Mismatch in {region}.{key}: expected {exp_val}, got {act_val}")
                    elif act_val != exp_val:
                        match = False
                        print(f"❌ Mismatch in {region}.{key}: expected {exp_val}, got {act_val}")
            else:
                match = False
                print(f"❌ Missing region in response: {region}")
        if match:
            print("✅ Response body matches expected metrics")
            # self.end_headers()
            # self.wfile.write(response.encode('utf-8'))
        else:
            print("❌ Response body does not match expected metrics")
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON response")