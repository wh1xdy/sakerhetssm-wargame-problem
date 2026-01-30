#! /bin/bash

# first inspect the zip 
file out.zip
7z l -slt out.zip #7zip is great in general

# identify zipcrypto and identify that a known plaintext attack can be used
# use bkcrack for this
bkcrack -L out.zip

# google if there is any known plaintext in jpeg file format
# https://en.wikipedia.org/wiki/List_of_file_signatures
# FF D8 FF E0 00 10 4A 46 49 46 00 01

# bkcrack -C out.zip -c flag.jpeg -x 0 ffd8ffe000104a4649460001

# you will get these keys
bkcrack -C out.zip -c flag.jpeg -k 0a317d16 3155b1e6 510edae2 -d image_decrypted.jpg
