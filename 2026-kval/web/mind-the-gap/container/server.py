from __future__ import annotations

from flask import Flask, request, jsonify, render_template
import sqlite3
import re
import os
import secrets

app = Flask(__name__)

DB_DIR = "/home/ctf/data"
DB_PATH = os.path.join(DB_DIR, "database.db")

VALID_QUERY_RE = re.compile(r"^[A-Za-z0-9 ]*$")

csrf_tokens = {}


def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY,
            question TEXT,
            answer TEXT,
            status TEXT
        )
        """
    )
    conn.execute("DELETE FROM faqs")
    faqs = [
        (
            "What is a CTF?",
            "CTF stands for Capture The Flag, a competition where participants solve security challenges.",
            "published",
        ),
        (
            "How do I get started with CTFs?",
            "Start with beginner-friendly platforms like TryHackMe, Hack The Box, or OverTheWire. Practice regularly, learn from writeups, and when you feel ready, compete in a professional competition like Säkerhets-SM!",
            "published",
        ),
        (
            "What categories exist in CTFs?",
            "Common categories include Web, Crypto, Pwn, Reverse Engineering, Forensics, and Misc.",
            "published",
        ),
        (
            "What tools do I need?",
            "Essential tools include Burp Suite, Wireshark, Ghidra, pwntools, and a Linux environment.",
            "published",
        ),
        (
            "How do teams communicate?",
            "Most teams use Discord or Slack for real-time collaboration during competitions.",
            "published",
        ),
        (
            "What is SQL injection?",
            "SQL injection is a code injection technique that exploits vulnerabilities in applications that construct SQL queries from user input without proper sanitization.",
            "published",
        ),
        (
            "What is XSS?",
            "Cross-Site Scripting (XSS) is a vulnerability that allows attackers to inject malicious scripts into web pages viewed by other users.",
            "published",
        ),
        (
            "What is a reverse shell?",
            "A reverse shell is a type of shell where the target machine initiates a connection back to the attacker's machine, bypassing firewalls that block incoming connections.",
            "published",
        ),
        (
            "What is buffer overflow?",
            "A buffer overflow occurs when a program writes more data to a buffer than it can hold, potentially overwriting adjacent memory and allowing code execution.",
            "published",
        ),
        (
            "What is steganography?",
            "Steganography is the practice of hiding secret data within ordinary files like images, audio, or text. Common in CTF forensics challenges.",
            "published",
        ),
        (
            "What is RSA?",
            "RSA is an asymmetric cryptographic algorithm used for secure data transmission. Many CTF crypto challenges involve exploiting weak RSA implementations.",
            "published",
        ),
        (
            "What is a hash function?",
            "A hash function converts input data into a fixed-size string of bytes. Common hashes include MD5, SHA-1, and SHA-256. Cracking hashes is common in CTFs.",
            "published",
        ),
        (
            "What is Burp Suite used for?",
            "Burp Suite is a web security testing tool used to intercept, modify, and replay HTTP requests. Essential for web exploitation challenges.",
            "published",
        ),
        (
            "What is Ghidra?",
            "Ghidra is a free reverse engineering tool developed by the NSA. It's used to analyze compiled binaries and understand their functionality.",
            "published",
        ),
        (
            "What is pwntools?",
            "Pwntools is a Python library designed for rapid exploit development. It simplifies tasks like connecting to services, crafting payloads, and shellcode generation.",
            "published",
        ),
        (
            "What is a format string vulnerability?",
            "A format string vulnerability occurs when user input is passed directly to printf-like functions, allowing attackers to read or write memory.",
            "published",
        ),
        (
            "What is ASLR?",
            "Address Space Layout Randomization (ASLR) is a security technique that randomizes memory addresses to make exploitation harder.",
            "published",
        ),
        (
            "What is a canary in binary exploitation?",
            "A stack canary is a random value placed before the return address to detect buffer overflows. If modified, the program terminates.",
            "published",
        ),
        (
            "What is ROP?",
            "Return-Oriented Programming (ROP) is an exploitation technique that chains together existing code snippets (gadgets) to execute arbitrary operations.",
            "published",
        ),
        (
            "What is a CTF writeup?",
            "A writeup is a detailed explanation of how a CTF challenge was solved. Reading writeups is one of the best ways to learn new techniques.",
            "published",
        ),
        (
            "What is the difference between jeopardy and attack-defense CTFs?",
            "Jeopardy CTFs have independent challenges worth points. Attack-defense CTFs involve teams defending their own services while attacking others.",
            "published",
        ),
        (
            "What is OSINT?",
            "Open Source Intelligence (OSINT) involves gathering information from publicly available sources. CTF OSINT challenges test research and investigation skills.",
            "published",
        ),
        (
            "What is a web shell?",
            "A web shell is a script uploaded to a web server that provides remote access and command execution capabilities to an attacker.",
            "published",
        ),
        (
            "What is directory traversal?",
            "Directory traversal is an attack that accesses files outside the intended directory by manipulating file paths with sequences like ../.",
            "published",
        ),
        (
            "What is SSRF?",
            "Server-Side Request Forgery (SSRF) tricks a server into making requests to unintended locations, potentially accessing internal resources.",
            "published",
        ),
        (
            "What is JWT?",
            "JSON Web Token (JWT) is a standard for securely transmitting information. CTF challenges often involve exploiting weak JWT implementations.",
            "published",
        ),
        (
            "What is a timing attack?",
            "A timing attack extracts secrets by measuring how long operations take. Even small time differences can leak information about correct values.",
            "published",
        ),
        (
            "What is the flag format in CTFs?",
            "Most CTFs use a specific flag format like CTF{...} or FLAG{...}. Always check the rules for the expected format.",
            "published",
        ),
        (
            "What is binwalk?",
            "Binwalk is a tool for analyzing and extracting embedded files from binary images. Essential for firmware and forensics challenges.",
            "published",
        ),
        (
            "What is John the Ripper?",
            "John the Ripper is a password cracking tool that supports various hash types and attack modes including dictionary and brute force.",
            "published",
        ),
        (
            "What is Hashcat?",
            "Hashcat is a fast password recovery tool that leverages GPU acceleration. Supports hundreds of hash algorithms.",
            "published",
        ),
        (
            "What is netcat?",
            "Netcat (nc) is a networking utility for reading and writing data across network connections. Often called the Swiss Army knife of networking.",
            "published",
        ),
        (
            "What is Wireshark?",
            "Wireshark is a network protocol analyzer used to capture and inspect network traffic. Essential for network forensics challenges.",
            "published",
        ),
        (
            "What is a sandbox escape?",
            "A sandbox escape is a technique to break out of a restricted environment and gain access to the underlying system.",
            "published",
        ),
        (
            "What is privilege escalation?",
            "Privilege escalation is the act of exploiting vulnerabilities to gain elevated access, such as moving from a normal user to root.",
            "published",
        ),
        (
            "What is the flag?",
            "SSM{r34r_l1n3_und3f3nd3d}",
            "draft",
        ),
    ]
    conn.executemany(
        "INSERT INTO faqs (question, answer, status) VALUES (?, ?, ?)", faqs
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/token", methods=["GET"])
def get_token():
    token = secrets.token_hex(32)
    csrf_tokens[token] = True
    return jsonify({"token": token})


@app.route("/api/validate", methods=["POST"])
def validate():
    data = request.get_json(force=True, silent=True) or {}
    query = str(data.get("query", ""))

    is_valid = VALID_QUERY_RE.fullmatch(query) is not None
    return jsonify({"valid": bool(is_valid)})


@app.route("/api/search", methods=["POST"])
def search():
    token = request.headers.get("X-CSRF-Token")
    if not token or token not in csrf_tokens:
        return jsonify({"error": "Invalid or missing CSRF token"}), 403
    del csrf_tokens[token]

    data = request.get_json(force=True, silent=True) or {}
    query = str(data.get("query", ""))

    if VALID_QUERY_RE.fullmatch(query):
        safe_literal = query.replace("'", "''")
        qexpr = f"'{safe_literal}'"
    else:
        qexpr = f"({query})"

    sql = f"""
WITH
  _q(v) AS (SELECT lower(coalesce({qexpr}, ''))),
  _p(p) AS (SELECT '%' || replace((SELECT v FROM _q), '%', '\\%') || '%')
SELECT question, answer
FROM faqs
WHERE status = 'published'
  AND lower(question) LIKE (SELECT p FROM _p) ESCAPE '\\'
"""

    conn = get_db()
    try:
        rows = conn.execute(sql).fetchall()
        return jsonify([{"question": r["question"], "answer": r["answer"]} for r in rows])
    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {e}\nSQL: {sql}"}), 400
    finally:
        conn.close()


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
