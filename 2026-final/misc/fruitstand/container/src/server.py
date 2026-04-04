################################################################################
################################################################################
###                                                                          ###
###                     THIS FILE DOES NOT EXIST                             ###
###                                                                          ###
################################################################################
###                                                                          ###
###                  This file is not part of the chall.                     ###
###                    It is just here to emulate the                        ###
###                     hardware part of the chall.                          ###
###                                                                          ###
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################

from flask import Flask, g, session, request, render_template, send_file

import json
import traceback
from pathlib import Path

import cv2, numpy as np, base64

from secret import flag_data

import hashlib, secrets
from datetime import timedelta

CHAR_NEWLINE = b'\n'

CHAR_PARTIAL_CUT = b'\x1bi'
CHAR_SEL_CODE_TABLE = b'\x1bt'
CHAR_PRINT_NV_BIT_IMAGE = b'\x1cp'
CHAR_DEFINE_NV_BIT_IMAGE = b'\x1cq'

LINE_WIDTH = 47

img_dir = Path('imgs')

def getImgData():
    settings = session['settings']
    if 'img_hash' not in settings:
        return None
    img_path: Path = img_dir / (settings['img_hash'] + '.json')
    try:
        img_data_text = img_path.read_text()
        img_data = json.loads(img_data_text)
        return img_data
    except:
        traceback.print_exc()
        return None

def putImgData(data):
    data_text = json.dumps(data)
    img_hash = hashlib.sha256(data_text.encode()).hexdigest()
    img_path: Path = img_dir / (img_hash + '.json')
    img_path.write_text(data_text)
    settings = session['settings']
    settings['img_hash'] = img_hash
    session['settings'] = settings

def bits_to_img(img_data):
    if not img_data: return '', { 'width': 0, 'height': 0 }
    x: int = int(img_data['x'])
    y: int = int(img_data['y'])
    data: bytes = base64.b64decode(img_data['data'])
    arr = []
    for iy in range(y):
        row = []
        for ix in range(x):
            index = iy + ix * y
            byte = data[index // 8]
            bit = 0 if (byte & (1 << 7 - (index % 8))) > 0 else 255
            row += [[bit] * 3]
        arr += [row]

    tmp_path = Path('/tmp/temp.png')
    cv2.imwrite(tmp_path.as_posix(), np.array(arr, dtype=np.uint8))

    img_bytes = tmp_path.read_bytes()
    tmp_path.unlink()

    b64 = base64.b64encode(img_bytes).decode()

    return 'data:image/png;base64,' + b64, { 'width': x, 'height': y }

def handle_printer_commands(commands: bytes):
    output = b''
    extra_data = {}
    i = 0
    while i < len(commands):
        if commands[i:].startswith(CHAR_PARTIAL_CUT):
            output += b'<hr>'
            i += len(CHAR_PARTIAL_CUT)
        elif commands[i:].startswith(CHAR_SEL_CODE_TABLE):
            i += len(CHAR_SEL_CODE_TABLE)
            new_settings = session['settings']
            new_settings['current_code_table'] = int(commands[i])
            session['settings'] = new_settings
        elif commands[i:].startswith(b'\n'):
            output += b'<br>'
        elif commands[i:].startswith(CHAR_PRINT_NV_BIT_IMAGE):
            offset = len(CHAR_PRINT_NV_BIT_IMAGE)
            n = commands[i + offset+0]
            m = commands[i + offset+1]
            assert m <= 0x33
            mode = m % 0x30
            assert 0 <= mode <= 3
            if 'image' not in extra_data: extra_data['image'] = []
            data_uri, size = bits_to_img(getImgData())

            output += f'<img style="aspect-ratio: {size["width"]} / {size["height"]}" src="{data_uri}" ><br>'.encode()
            i += len(CHAR_PRINT_NV_BIT_IMAGE) + 2
        elif commands[i:].startswith(CHAR_DEFINE_NV_BIT_IMAGE):
            offset = len(CHAR_DEFINE_NV_BIT_IMAGE)
            n  = commands[i + offset+0]
            xL = commands[i + offset+1]
            xH = commands[i + offset+2]
            yL = commands[i + offset+3]
            yH = commands[i + offset+4]
            x = (xH << 8) + xL
            y = (yH << 8) + yL
            assert n == 1
            assert x <= 1023
            assert y <= 288
            data_len = x * y * 8 * 8
            i += len(CHAR_DEFINE_NV_BIT_IMAGE) + 5
            putImgData({
                'x': x * 8,
                'y': y * 8,
                'data': base64.b64encode(commands[i:i+data_len]).decode()
            })
            i += data_len
        else:
            char = commands[i:i+1]\
                .replace(b'&', b'&amp;')\
                .replace(b'<', b'&lt;')\
                .replace(b'>', b'&gt;')\
                .replace(b"'", b'&apos;')\
                .replace(b'"', b'&quot;')
            if char[0] > 0x80:
                if session['settings']["current_code_table"] == 2 and char == b'\xcf':
                    char = '¤'.encode()
            try:
                index_of_br = output[::-1].index(b'<br>'[::-1])
                if index_of_br >= LINE_WIDTH:
                    output += b'<br>'
            except ValueError: pass
            output += char
        i += 1
    return output, extra_data

def actually_print(data):
    data = data
    lines = data.count(b"\n")
    data += b"\n" * max(5, 8 - lines)
    data += CHAR_PARTIAL_CUT
    print("=" * 60 + f"\n{data.rstrip(CHAR_PARTIAL_CUT + CHAR_NEWLINE).decode(errors='ignore')}\n" + "=" * 60)
    return send_printer_data(data)

def receipt_to_html(receipt_data: bytes):
    plaintext, extra_data = handle_printer_commands(receipt_data)

    return plaintext.decode(errors='ignore'), extra_data

def send_printer_data(receipt_data: bytes):
    html_data, extra_data = receipt_to_html(receipt_data)
    return json.dumps({'data': html_data, 'extra_data': extra_data})
    for i in range(0, len(receipt_data), 1024):
        pass
        #printer_endpoint.write(data[i : i + 1024])

def print_err(s):
    session['order'] = []
    return actually_print(f"ERROR: {s}\n\nCurrent order has been cleared.".encode())

def cmd_select_product(data):
    if "product" not in data:
        return print_err("Must specify product.")

    p = Path("products") / data["product"]
    if p.is_dir():
        hidden = [ 'html', 'server.py', '__pycache__' ]
        return actually_print(("Available products:\n" + "\n".join([c.name for c in p.iterdir() if not c.name in hidden])).encode())

    if not p.is_file():
        return print_err("Could not load product.")

    if "secret" in data["product"]:
        return print_err("This is a fruit stand, not a flag szop")

    raw_data = p.read_text()[: 1024 * 5]
    try:
        product_data = json.loads(raw_data)
    except:
        return print_err(f'Could not read product, "{raw_data}" is not valid json.')

    if "name" not in product_data or "cost" not in product_data or not isinstance(product_data["cost"], float):
        return print_err("Invalid product.")

    new_order = session['order']
    new_order.append(product_data)
    session['order'] = new_order

    return json.dumps({'status': 'added'})


def cmd_complete_order():
    receipt = b""
    cost = 0
    for product in session['order']:
        cost += product["cost"]
        c = f"{product['cost']:.2f}".encode()
        receipt += product["name"].encode() + b" " + b"." * (45 - len(product["name"]) - len(c)) + b" " + c + b"\n"
    receipt += b"\nTotal: " + f"{cost:.2f}".encode() + b" \x1bt\x02\xcf\n\nThanks for shopping at the SSM fruit stand!"
    responseContent = actually_print(receipt)
    session['order'] = []
    return responseContent

app = Flask(__name__, template_folder='html')

app.secret_key = hashlib.sha256(flag_data).digest() + hashlib.sha256(flag_data[::-1]).digest()
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

@app.before_request
def before_request():
    if 'order' not in session:
        session['order'] = []
    if 'settings' not in session:
        session['settings'] = {'current_code_table': 0}

@app.route("/")
def index():
    send_printer_data(b"\x1cq\x012\x00}\x00" + flag_data)
    return render_template('index.html')

@app.route('/jsQR.js')
def jsqr():
    return send_file('html/jsQR.js')

@app.post("/scan")
def scan():
    try:
        raw_data = request.data

        try:
            data = json.loads(raw_data.decode())
        except UnicodeDecodeError:
            return print_err("Scan data is not valid unicode.")
        except json.JSONDecodeError:
            return print_err("Scan data is not valid json.")

        if "type" not in data:
            return print_err("Command does not include type.")

        if data["type"] == "select_product":
            return cmd_select_product(data)
        elif data["type"] == "complete_order":
            return cmd_complete_order()
        elif data["type"] == "admin_custom_product":
            if (
                "product" not in data
                or "name" not in data["product"]
                or "cost" not in data["product"]
                or not isinstance(
                    data["product"]["cost"],
                    float,
                )
            ):
                return 'error', 400

            new_order = session['order']
            new_order.append(data["product"])
            session['order'] = new_order

            return json.dumps({'status': 'Hej'})
        else:
            return print_err("Command not recognized.")
    except Exception as e:
        traceback.print_exc()
        session['order'] = []
        return 'Exception'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
