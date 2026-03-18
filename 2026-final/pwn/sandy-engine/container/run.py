#!/usr/bin/env python3
import base64
import tempfile
import subprocess
import sys
import os

D8_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d8")
TIMEOUT = 10

def main():
    print("Send your base64-encoded JS (one line):")
    try:
        encoded = input().strip()
    except EOFError:
        sys.exit(1)

    try:
        js = base64.b64decode(encoded)
    except Exception:
        print("Invalid base64")
        sys.exit(1)

    with tempfile.NamedTemporaryFile(suffix=".js", delete=True) as f:
        f.write(js)
        f.flush()
        try:
            subprocess.run(
                [D8_PATH, "--expose-memory-corruption-api", f.name],
                timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            print("Timeout")

if __name__ == "__main__":
    main()
