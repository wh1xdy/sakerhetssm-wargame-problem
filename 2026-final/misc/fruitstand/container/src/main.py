import json
import traceback
from pathlib import Path

import usb
from secret import flag_data

printer_dev = usb.core.find(idVendor=0x1504, idProduct=0x0103)
try:
    printer_dev.detach_kernel_driver(0)
except usb.core.USBError:
    pass
_, printer_endpoint = printer_dev.get_active_configuration()[(0, 0)].endpoints()

scanner_dev = usb.core.find(idVendor=0x1EAB, idProduct=0x8210)
try:
    scanner_dev.detach_kernel_driver(0)
except usb.core.USBError:
    pass
scanner_endpoint, _ = scanner_dev.get_active_configuration()[(0, 0)].endpoints()

order = []


def actually_print(data):
    data = data
    lines = data.count(b"\n")
    data += b"\n" * max(5, 8 - lines)
    data += b"\x1bi"
    print("=" * 60 + f"\n{data.rstrip(b"\x1bi\n").decode(errors="ignore")}\n" + "=" * 60)
    send_printer_data(data)


def send_printer_data(data):
    for i in range(0, len(data), 1024):
        printer_endpoint.write(data[i : i + 1024])


def print_err(s):
    global order
    order = []
    actually_print(f"ERROR: {s}\n\nCurrent order has been cleared.".encode())


def cmd_select_product(data):
    if "product" not in data:
        print_err("Must specify product.")
        return

    p = Path("products") / data["product"]
    if p.is_dir():
        actually_print(("Available products:\n" + "\n".join([c.name for c in p.iterdir()])).encode())
        return

    if not p.is_file():
        print_err("Could not load product.")
        return

    if "secret" in data["product"]:
        print_err("This is a fruit stand, not a flag szop")
        return

    raw_data = p.read_text()[: 1024 * 5]
    try:
        product_data = json.loads(raw_data)
    except:
        print_err(f'Could not read product, "{raw_data}" is not valid json.')
        return

    if "name" not in product_data or "cost" not in product_data or not isinstance(product_data["cost"], float):
        print_err("Invalid product.")
        return

    order.append(product_data)


def cmd_complete_order():
    global order
    receipt = b""
    cost = 0
    for product in order:
        cost += product["cost"]
        c = f"{product["cost"]:.2f}".encode()
        receipt += product["name"].encode() + b" " + b"." * (45 - len(product["name"]) - len(c)) + b" " + c + b"\n"
    receipt += b"\nTotal: " + f"{cost:.2f}".encode() + b" \x1bt\x02\xcf\n\nThanks for shopping at the SSM fruit stand!"
    order = []
    actually_print(receipt)


send_printer_data(b"\x1cq\x012\x00}\x00" + flag_data)

while True:
    try:
        try:
            raw_data = b""
            while True:
                r = scanner_endpoint.read(64).tobytes()
                raw_data += r[2:58]
                if r[-1] != 1:
                    break
        except usb.core.USBTimeoutError:
            continue
        raw_data = raw_data.rstrip(b"\x00").rstrip()
        print("SCANNED:", raw_data)

        try:
            data = json.loads(raw_data.decode())
        except UnicodeDecodeError:
            print_err("Scan data is not valid unicode.")
            continue
        except json.JSONDecodeError:
            print_err("Scan data is not valid json.")
            continue

        if "type" not in data:
            print_err("Command does not include type.")
            continue

        if data["type"] == "select_product":
            cmd_select_product(data)
        elif data["type"] == "complete_order":
            cmd_complete_order()
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
                continue
            order.append(data["product"])
        else:
            print_err("Command not recognized.")
    except Exception as e:
        traceback.print_exc()
        order = []
