import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from flask import Flask, request, send_file, send_from_directory

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bygg binärer med Mulle Meck</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">
  <style>
    html { background-color: #1a1a2e; }
    body {
      min-height: 100vh; display: flex; align-items: center; justify-content: center;
      position: relative;
    }
    body::before {
      content: "";
      position: fixed; inset: 0;
      background: url("/mulle.png") center/cover no-repeat;
      opacity: 0.2;
      z-index: -1;
    }
    .box { max-width: 500px; width: 100%; background-color: #16213e; border: 1px solid #0f3460; }
    .title, .label { color: #e2e8f0 !important; }
    .subtitle { color: #94a3b8 !important; }
    .file-cta { background-color: #0f3460; border-color: #1a4a8a; color: #e2e8f0; }
    .file-cta:hover { background-color: #1a4a8a; }
    .file-name { background-color: #1a1a2e; border-color: #0f3460; color: #94a3b8; max-width: 300px; }
    .button.is-link { background-color: #00d1b2; color: #1a1a2e; font-weight: 600; }
    .button.is-link:hover { background-color: #00c4a7; }
  </style>
</head>
<body>
  <div class="box">
    <h1 class="title is-3 has-text-centered">Bygg en binär</h1>
    <p class="subtitle is-6 has-text-centered"><br>Alla vet att statiska binärer är de mulligaste.<br></p>
    <form action="/compile" method="post" enctype="multipart/form-data">
      <div class="field">
        <label class="label">Slanga upp en .zip med dina mojänger!</label>
        <div class="file has-name is-fullwidth">
          <label class="file-label">
            <input class="file-input" type="file" name="file" accept=".zip" required
                   onchange="this.closest('.file').querySelector('.file-name').textContent = this.files[0].name">
            <span class="file-cta">
              <span class="file-label">Välj pryl...</span>
            </span>
            <span class="file-name">Ingen fil vald</span>
          </label>
        </div>
      </div>
      <div class="field mt-4">
        <button class="button is-link is-fullwidth" type="submit">Kompilera</button>
      </div>
    </form>
  </div>
</body>
</html>"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/mulle.png")
def mulle():
    return send_from_directory(".", "mulle.png")


@app.route("/compile", methods=["POST"])
def compile():
    f = request.files.get("file")
    if f is None:
        return "Du skickade ingen fil\n", 400

    if not f.filename.endswith(".zip"):
        return "Endast .zip tack\n", 400

    tmp = tempfile.mkdtemp()
    out_bin = os.path.join(tmp, "output")

    try:
        zip_path = os.path.join(tmp, "upload.zip")
        f.save(zip_path)

        try:
            with zipfile.ZipFile(zip_path) as zf:
                dest = os.path.join(tmp, "src")
                for info in zf.infolist():
                    zf.extract(info, dest)
        except zipfile.BadZipFile:
            return "Fel på zip arkivet\n", 400

        src_dir = os.path.join(tmp, "src")

        if not os.path.isfile(os.path.join(src_dir, "go.mod")):
            return "go.mod krävs!\n", 400

        env = os.environ.copy()
        env["CGO_ENABLED"] = "0"

        result = subprocess.run(
            ["go", "build", "-o", out_bin, "."],
            cwd=src_dir,
            env=env,
            capture_output=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Det där gick åt skogen!\n", 400

        return send_file(out_bin, mimetype="application/octet-stream",
                         as_attachment=True, download_name="output")

    except subprocess.TimeoutExpired:
        return "Det tog en jäkla tid. Struntar i det här nu.\n", 408

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
