package main

import (
	"crypto/aes"
	"crypto/cipher"
	"encoding/hex"
	"fmt"
)

const keyLength = 16

func decrypt(cipherText, key, IV []byte) bool {
	block, err := aes.NewCipher(key)
	if err != nil {
		fmt.Println("failed to create cipher")
        return false
	}
	l := len(cipherText)
	plainText := make([]byte, l)
	mode := cipher.NewCBCDecrypter(block, IV)
	mode.CryptBlocks(plainText, cipherText)
	last := plainText[l-1]
	if last == 0 || int(last) > l {
		return false
	}
	paddingStart := l - int(last)
	for i := paddingStart; i < l; i++ {
		if plainText[i] != last {
			return false
		}
	}
	for i := 0; i < paddingStart; i++ {
		if plainText[i] < 32 || plainText[i] > 126 {
			return false
		}
	}
	fmt.Println(string(plainText[:paddingStart]))
	return true
}

func run(key []byte) bool {
	IV, _ := hex.DecodeString("d6b3ec1309b9ea8186a58cb2d38ded80")
	cipherText, _ := hex.DecodeString("bf3ff258b0ac7c8c0cd17b3cbdaf350e3dfd1b41fb225941215a81a8e2ad5fb5ce5a71b6be36ed1eb8fe601b137bbd76")
	if decrypt(cipherText, key, IV) {
		fmt.Println("decoding succeeded")
		fmt.Printf("%x\n", key)
		return true
	}
	return false
}

func generateKey(i int) []byte {
	key := make([]byte, keyLength)
	j := 0
	for i > 0 {
		if i&1 == 1 {
			key[j] = 4
		}
		i >>= 1
		j += 1
	}
	return key
}

func main() {
	for i := 0; i <= 0xffff; i++ {
		key := generateKey(i)
		run(key)
	}
}
