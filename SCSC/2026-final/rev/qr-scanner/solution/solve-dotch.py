import zipfile
import sys
import zlib
from pathlib import Path

from PIL import Image
import zxingcpp

cwd = Path(__file__).resolve().parent
apk_src = cwd.parent / "qrScanner.apk"
so_file_name = "libqrScanner_arm64-v8a.so"
so_file_dst = cwd / so_file_name
extracted_out_dir = cwd / "extracted"
flag_path = extracted_out_dir / "resources" / "flag.png"

# Direct pointers from qRegisterResourceData usage in qInitResources_resources.
TREE_PTR = 0x2B1DE
NAMES_PTR = 0x2B220
PAYLOAD_PTR = 0x2B252


def extract_so_file_from_apk():
    # The path to the .so file inside the APK
    so_file_zip_dir = "lib/arm64-v8a/"
    so_file_zip_path = so_file_zip_dir + so_file_name
    # The destination path for the extracted .so file
    # Extract the .so file from the APK using zipfile
    with zipfile.ZipFile(apk_src, "r") as zip_ref:
        # Extract the .so file to the destination path
        zip_ref.extract(so_file_zip_path, cwd)
        # Move the extracted .so file to the desired location
        extracted_so_file = cwd / so_file_zip_path
        extracted_so_file.rename(so_file_dst)
        # Remove the now empty directories
        (cwd / so_file_zip_dir).rmdir()

    print(f"Extracted {so_file_dst} from {apk_src}")


def load_qresource_class():
    pkg_dir = cwd / "binja-qresource"
    if str(pkg_dir) not in sys.path:
        sys.path.insert(0, str(pkg_dir))

    from qresource import QResource

    return QResource


def extract_resource_files():
    with open(so_file_dst, "rb") as f:
        content = f.read()
        tree_data = content[TREE_PTR:]
        names_data = content[NAMES_PTR:]
        payload_data = content[PAYLOAD_PTR:]
        print(f"Tree pointer: {TREE_PTR:#x}")
        print(f"Names pointer: {NAMES_PTR:#x}")
        print(f"Payload pointer: {PAYLOAD_PTR:#x}")

        QResource = load_qresource_class()
        files = QResource().get_files(tree_data, names_data, payload_data)
        return files


def maybe_decompress_resource(data: bytes) -> bytes:
    # zlib-wrapped stream (common for Qt compressed resources)
    if len(data) >= 2 and data[0] == 0x78:
        try:
            return zlib.decompress(data)
        except zlib.error:
            pass

    # zstd frame magic; optional dependency in this workspace.
    if len(data) >= 4 and data[:4] == bytes.fromhex("28B52FFD"):
        try:
            import zstandard as zstd

            return zstd.ZstdDecompressor().decompress(data)
        except Exception:
            pass

    return data


def write_files(files, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        # Names are in Qt style like :/dir/file.ext
        rel = f.name[2:]
        dst = out_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(maybe_decompress_resource(f.data))


# See: https://wiki.qt.io/QtResources
# From: https://observablehq.com/@mblsha/qresource-blob-parser (JS parser for .qrc files)
#
#     <RCC version="1.0">
#     <qresource prefix="/">
#         <file>res/1.txt</file>
#         ...
#         <file>res/foodir/3.txt</file>
#     </qresource>
#     </RCC>
#
# This file is integrated into the binary using the method shown:
#
#     qRegisterResourceData(3, qt_resource_struct, qt_resource_name, qt_resource_data);
#
# In `libqrScanner_arm64-v8a.so` we can find the following code that references the flag data offset:
#    .text:0x00000000000A6BBC int32_t __cdecl qInitResources_resources( void )
#    .text:0x00000000000A6BBC {
#    .text:0x00000000000A6BBC    uint64_t local_0x8;
#    .text:0x00000000000A6BBC
#    .text:0x00000000000A6BBC    FD7BBFA9             stp x29, x30, [local_0x8]!
#    .text:0x00000000000A6BC0    FD030091             mov x29, sp
#    .text:0x00000000000A6BC4    1F2003D5             nop
#    .text:0x00000000000A6BC8    A130C250             adr x1, data_0x2B1DE
#    .text:0x00000000000A6BCC    1F2003D5             nop
#    .text:0x00000000000A6BD0    8232C210             adr x2, data_0x2B220
#    .text:0x00000000000A6BD4    1F2003D5             nop
#    .text:0x00000000000A6BD8    A333C250             adr x3, (string_flagpng+0xF); "flag.png"
#    .text:0x00000000000A6BDC    60008052             movz w0, #0x3
#    .text:0x00000000000A6BE0    887D0294             bl qRegisterResourceData; void __cdecl( int p1, unsigned char * p2, unsigned char * p3, unsigned char * p4 )
#    .text:0x00000000000A6BE4    20008052             movz w0, #0x1
#    .text:0x00000000000A6BE8    FD7BC1A8             ldp x29, x30, [local_0x8], #0x10
#    .text:0x00000000000A6BEC    C0035FD6             ret
#    .text:0x00000000000A6BEC }


def main() -> None:
    if not so_file_dst.exists():
        extract_so_file_from_apk()
    files = extract_resource_files()
    print(f"Extracted entries: {len(files)}")
    write_files(files, extracted_out_dir)

    if not flag_path.exists():
        raise FileNotFoundError(f"Expected barcode image not found: {flag_path}")

    image = Image.open(flag_path)
    results = zxingcpp.read_barcodes(image)
    if not results:
        raise RuntimeError("No barcode detected in extracted flag image")

    print("Decoded barcode content:")
    for r in results:
        print(r.text)


if __name__ == "__main__":
    main()
