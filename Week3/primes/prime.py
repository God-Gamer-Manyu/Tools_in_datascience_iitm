#!/usr/bin/env python3
"""Compute primes and print the 10th prime. Also append a log entry to ./logs/prime.log

Usage: python prime.py
"""

import math
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs', 'prime.log')
# Normalize path: the logs folder is at workspace root 'logs'
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'prime.log'))


def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    r = int(math.sqrt(n))
    for i in range(3, r + 1, 2):
        if n % i == 0:
            return False
    return True


def nth_prime(n: int) -> int:
    count = 0
    candidate = 1
    while True:
        candidate += 1
        if is_prime(candidate):
            count += 1
            if count == n:
                return candidate


if __name__ == '__main__':
    N = 10
    p = nth_prime(N)
    output = f"The {N}th prime is: {p}"
    print(output)

    # Ensure logs directory exists
    log_dir = os.path.dirname(LOG_PATH)
    os.makedirs(log_dir, exist_ok=True)

    # Append a log entry
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - INFO - prime.py printed: {output}\n")
