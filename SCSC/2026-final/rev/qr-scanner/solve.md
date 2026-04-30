# Solve Instellate

For whatever unknown reasons tools like `github.com/axstin/qtextract` does not work. It works on other arm64-v8a `so` files but not this one. So you will need to do what it does manually.

Steps:
- Find `qRegisterResourceData`
- Look for usage of `qRegisterResourceData`
- Look for usage that contains something with `flag.png` ()
- Get bytes for `qt_resource_data` and decompress with zstd
- Scan the extracted image and get the flag