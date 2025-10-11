import json
import numpy as np
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any

data = [
  {
    "region": "apac",
    "service": "checkout",
    "latency_ms": 147.63,
    "uptime_pct": 97.259,
    "timestamp": 20250301
  },
  {
    "region": "apac",
    "service": "support",
    "latency_ms": 197.89,
    "uptime_pct": 99.411,
    "timestamp": 20250302
  },
  {
    "region": "apac",
    "service": "payments",
    "latency_ms": 127.76,
    "uptime_pct": 97.465,
    "timestamp": 20250303
  },
  {
    "region": "apac",
    "service": "recommendations",
    "latency_ms": 184.26,
    "uptime_pct": 97.952,
    "timestamp": 20250304
  },
  {
    "region": "apac",
    "service": "recommendations",
    "latency_ms": 193.97,
    "uptime_pct": 98.531,
    "timestamp": 20250305
  },
  {
    "region": "apac",
    "service": "payments",
    "latency_ms": 131.2,
    "uptime_pct": 97.381,
    "timestamp": 20250306
  },
  {
    "region": "apac",
    "service": "checkout",
    "latency_ms": 128.25,
    "uptime_pct": 98.898,
    "timestamp": 20250307
  },
  {
    "region": "apac",
    "service": "catalog",
    "latency_ms": 122.09,
    "uptime_pct": 98.48,
    "timestamp": 20250308
  },
  {
    "region": "apac",
    "service": "recommendations",
    "latency_ms": 224.91,
    "uptime_pct": 99.444,
    "timestamp": 20250309
  },
  {
    "region": "apac",
    "service": "support",
    "latency_ms": 177.43,
    "uptime_pct": 97.114,
    "timestamp": 20250310
  },
  {
    "region": "apac",
    "service": "analytics",
    "latency_ms": 184.76,
    "uptime_pct": 98.865,
    "timestamp": 20250311
  },
  {
    "region": "apac",
    "service": "analytics",
    "latency_ms": 184.87,
    "uptime_pct": 98.033,
    "timestamp": 20250312
  },
  {
    "region": "emea",
    "service": "recommendations",
    "latency_ms": 111.58,
    "uptime_pct": 97.406,
    "timestamp": 20250301
  },
  {
    "region": "emea",
    "service": "analytics",
    "latency_ms": 148.95,
    "uptime_pct": 99.214,
    "timestamp": 20250302
  },
  {
    "region": "emea",
    "service": "analytics",
    "latency_ms": 196.32,
    "uptime_pct": 97.898,
    "timestamp": 20250303
  },
  {
    "region": "emea",
    "service": "payments",
    "latency_ms": 125,
    "uptime_pct": 98.201,
    "timestamp": 20250304
  },
  {
    "region": "emea",
    "service": "checkout",
    "latency_ms": 141.87,
    "uptime_pct": 98.849,
    "timestamp": 20250305
  },
  {
    "region": "emea",
    "service": "payments",
    "latency_ms": 123.62,
    "uptime_pct": 99.168,
    "timestamp": 20250306
  },
  {
    "region": "emea",
    "service": "recommendations",
    "latency_ms": 133.48,
    "uptime_pct": 98.523,
    "timestamp": 20250307
  },
  {
    "region": "emea",
    "service": "analytics",
    "latency_ms": 189.87,
    "uptime_pct": 99.207,
    "timestamp": 20250308
  },
  {
    "region": "emea",
    "service": "recommendations",
    "latency_ms": 138.89,
    "uptime_pct": 99.109,
    "timestamp": 20250309
  },
  {
    "region": "emea",
    "service": "catalog",
    "latency_ms": 185.6,
    "uptime_pct": 98.508,
    "timestamp": 20250310
  },
  {
    "region": "emea",
    "service": "checkout",
    "latency_ms": 197.74,
    "uptime_pct": 97.164,
    "timestamp": 20250311
  },
  {
    "region": "emea",
    "service": "support",
    "latency_ms": 127.38,
    "uptime_pct": 97.903,
    "timestamp": 20250312
  },
  {
    "region": "amer",
    "service": "recommendations",
    "latency_ms": 183.01,
    "uptime_pct": 97.607,
    "timestamp": 20250301
  },
  {
    "region": "amer",
    "service": "support",
    "latency_ms": 128.24,
    "uptime_pct": 98.963,
    "timestamp": 20250302
  },
  {
    "region": "amer",
    "service": "recommendations",
    "latency_ms": 120.26,
    "uptime_pct": 97.803,
    "timestamp": 20250303
  },
  {
    "region": "amer",
    "service": "recommendations",
    "latency_ms": 180.68,
    "uptime_pct": 97.196,
    "timestamp": 20250304
  },
  {
    "region": "amer",
    "service": "checkout",
    "latency_ms": 143.73,
    "uptime_pct": 99.293,
    "timestamp": 20250305
  },
  {
    "region": "amer",
    "service": "catalog",
    "latency_ms": 160.76,
    "uptime_pct": 97.103,
    "timestamp": 20250306
  },
  {
    "region": "amer",
    "service": "analytics",
    "latency_ms": 175.87,
    "uptime_pct": 99.343,
    "timestamp": 20250307
  },
  {
    "region": "amer",
    "service": "support",
    "latency_ms": 113.97,
    "uptime_pct": 99.147,
    "timestamp": 20250308
  },
  {
    "region": "amer",
    "service": "catalog",
    "latency_ms": 175.99,
    "uptime_pct": 97.472,
    "timestamp": 20250309
  },
  {
    "region": "amer",
    "service": "analytics",
    "latency_ms": 188.39,
    "uptime_pct": 98.358,
    "timestamp": 20250310
  },
  {
    "region": "amer",
    "service": "checkout",
    "latency_ms": 116.39,
    "uptime_pct": 99.114,
    "timestamp": 20250311
  },
  {
    "region": "amer",
    "service": "support",
    "latency_ms": 129.62,
    "uptime_pct": 97.185,
    "timestamp": 20250312
  }
]

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            regions = body.get('regions', [])
            threshold_ms = body.get('threshold_ms', 180)

            metrics = {}
            for region in regions:
                region_data = [d for d in data if d['region'] == region]
                if not region_data:
                    continue

                latencies = np.array([d['latency_ms'] for d in region_data])
                uptimes = np.array([d['uptime_pct'] for d in region_data])

                avg_latency = np.mean(latencies)
                p95_latency = np.percentile(latencies, 95)
                avg_uptime = np.mean(uptimes)
                breaches = np.sum(latencies > threshold_ms)

                metrics[region] = {
                    'avg_latency': round(float(avg_latency), 2),
                    'p95_latency': round(float(p95_latency), 2),
                    'avg_uptime': round(float(avg_uptime), 2),
                    'breaches': int(breaches)
                }

            response = json.dumps(metrics)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode('utf-8'))

    def do_GET(self):
        self.send_response(405)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()