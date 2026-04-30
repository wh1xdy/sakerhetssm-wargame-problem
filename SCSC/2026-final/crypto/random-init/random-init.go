package main

import (
	"bufio"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"fmt"
	"os"
	"strings"
)

const keyLength = 16

func superSecureKeyGeneration() []byte {
	key := make([]byte, keyLength)
	extraRand := make([]byte, keyLength)
        // Use twice the random bits
	rand.Read(key)
	rand.Read(extraRand)
	for i := 0; i < keyLength; i++ {
		// Securely shuffle (shift by primes)
		k := ((key[i] >> 3) ^ (extraRand[i] << 7)) >> 5
		key[i] = k
	}
	return key
}

func randomInitIV() []byte {
	IV := make([]byte, keyLength)
	rand.Read(IV)
	return IV
}

func readAndPad() []byte {
	reader := bufio.NewReader(os.Stdin)
	messageStr, err := reader.ReadString('\n')
	if err != nil {
		fmt.Println("could not read line")
		panic(err)
	}
	messageStr = strings.Trim(messageStr, "\r\n")
	message := []byte(messageStr)
	l := len(message)
	numBlocks := l/aes.BlockSize + 1
	paddedLength := numBlocks * aes.BlockSize
	extraBytes := paddedLength - l
	ret := make([]byte, paddedLength)
	copy(ret, message)
	for i := l; i < paddedLength; i++ {
		ret[i] = byte(extraBytes)
	}
	return ret
}

func run() {
	key := superSecureKeyGeneration()
	IV := randomInitIV()
	// Read our secret message
	plainText := readAndPad()
	// Encrypt our secret message
	block, err := aes.NewCipher(key)
	if err != nil {
		fmt.Println("failed to create cipher")
		panic(err)
	}
	cipherText := make([]byte, len(plainText))
	mode := cipher.NewCBCEncrypter(block, IV)
	mode.CryptBlocks(cipherText, plainText)
	fmt.Printf("IV=%x\ncipher=%x\n", IV, cipherText)
}

func main() {
	run()
}
