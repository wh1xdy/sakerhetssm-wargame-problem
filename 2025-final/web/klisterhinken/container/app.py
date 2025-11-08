from flask import Flask, request, g, render_template, redirect, jsonify
from hashlib import sha256
import sqlite3
import os

app = Flask(__name__)

DATABASE = "notes.db"

TITLE = "Admin Note"
FLAG = os.environ["FLAG"]

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE,timeout=5)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY, title TEXT, body TEXT)"""
        )
        cursor.execute(
            "INSERT INTO notes (id, title, body) VALUES (?, ?, ?)",
            (generateId(TITLE, FLAG), TITLE, FLAG),
        )
        get_db().commit()


def generateId(title, body):
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*) FROM notes")
    try:
        r = f"{sha256(body.encode()[:4]).hexdigest()[:8]}{id(cursor.fetchone()[0] % 256):x}{sum(map(ord,title))^0x1337:x}"
    except:
        cursor.close()
        raise
    return r


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def create_note():
    title = request.form.get("title")
    body = request.form.get("body")
    note_id = generateId(title, body)
    cursor = get_db().cursor()
    try:
        cursor.execute(
            "INSERT INTO notes (id, title, body) VALUES (?, ?, ?)",
            (note_id, title, body),
        )
        cursor.close()
    except sqlite3.IntegrityError:
        cursor.close()
        return jsonify({"message": "Note not unique"}), 500
    get_db().commit()
    return redirect(note_id)


@app.route("/<note_id>", methods=["GET"])
def get_note_by_id(note_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    if note is None:
        return jsonify({"message": "Note not found"}), 404
    if note[2] == FLAG:
        return render_template("win.html",note=note)
    return render_template("note.html", note=note)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=3000)
