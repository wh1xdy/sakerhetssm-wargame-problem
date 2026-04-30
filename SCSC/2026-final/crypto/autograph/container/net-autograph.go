package main

import (
	"bufio"
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"errors"
	"fmt"
	"net"
	"strings"
)

const keyLength = 32

var celebrities = []string{"Rivest", "Shamir", "Adleman", "Shor", "Shanks", "Daemen", "Rijmen"}

func pad(s []byte) []byte {
	l := len(s)
	paddedLength := (l/aes.BlockSize + 1) * aes.BlockSize
	paddingLength := paddedLength - l
	ret := make([]byte, paddedLength)
	copy(ret, s)
	for i := l; i < paddedLength; i++ {
		ret[i] = byte(paddingLength)
	}
	return ret
}

// signed plainText -> IV || encrypt( signed plainText || padding )
// where || is concat
func encrypt(plainText, key []byte) ([]byte, error) {
	padded := pad(plainText)
	IV := make([]byte, aes.BlockSize)
	rand.Read(IV)
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, errors.New("failed to create aes cipher")
	}
	cipherText := make([]byte, aes.BlockSize+len(padded))
	copy(cipherText, IV)
	mode := cipher.NewCBCEncrypter(block, IV)
	mode.CryptBlocks(cipherText[aes.BlockSize:], padded)
	return cipherText, nil
}

// plainText -> plainText || signature
func sign(c string, key []byte) []byte {
	mac := hmac.New(sha256.New, key)
	mac.Write([]byte(c))
	signature := mac.Sum(nil)
	ret := append([]byte(c), signature...)
	return ret
}

func freeCollection(d map[string][]byte, conn net.Conn) {
	for i := 0; i < 3; i++ {
		c := celebrities[i]
		conn.Write([]byte(fmt.Sprintf(" %15s : %x\n", c, d[c])))
	}
}

func premiumCollection(d map[string][]byte, key []byte, reader *bufio.Reader, conn net.Conn) {
	conn.Write([]byte("Enter the master key in hex > "))
	fromUser, _ := reader.ReadString('\n')
	fromUser = strings.Trim(fromUser, " \t\r\n")
	userKey, err := hex.DecodeString(fromUser)
	if err != nil {
		conn.Write([]byte("bad hex\n"))
		return
	}
	if subtle.ConstantTimeCompare(userKey, key) != 1 {
		conn.Write([]byte("bad key\n"))
		return
	}
	for i := 3; i < len(celebrities); i++ {
		c := celebrities[i]
		conn.Write([]byte(fmt.Sprintf(" %15s : %x\n", c, d[c])))
	}
}

func decrypt(sig, key []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	l := len(sig)
	if l == 0 || l%aes.BlockSize != 0 {
		return nil, errors.New("bad length")
	}
	IV := sig[:aes.BlockSize]
	plainText := make([]byte, l-aes.BlockSize)
	mode := cipher.NewCBCDecrypter(block, IV)
	mode.CryptBlocks(plainText, sig[aes.BlockSize:])
	l -= aes.BlockSize
	if l-1 < 0 {
		return nil, errors.New("bad length")
	}
	last := plainText[l-1]
	if last == 0 || int(last) > l {
		return nil, errors.New("bad pad")
	}
	paddingStart := l - int(last)
	for i := paddingStart; i < l; i++ {
		if plainText[i] != last {
			return nil, errors.New("bad pad")
		}
	}
	return plainText[:paddingStart], nil
}

func verifySignature(plainText, key []byte) bool {
	l := len(plainText)
	if l <= keyLength {
		return false
	}
	autographLength := l - keyLength
	autograph := plainText[:autographLength]
	autographMac := plainText[autographLength:]
	mac := hmac.New(sha256.New, key)
	mac.Write(autograph)
	expectedMac := mac.Sum(nil)
	return hmac.Equal(expectedMac, autographMac)
}

func verify(key []byte, reader *bufio.Reader, conn net.Conn) {
	conn.Write([]byte("Enter your signature in hex > "))
	signature, _ := reader.ReadString('\n')
	signature = strings.Trim(signature, " \t\r\n")
	sig, err := hex.DecodeString(signature)
	if err != nil {
		conn.Write([]byte("bad hex\n"))
		return
	}
	if len(sig) == 0 || len(sig)%aes.BlockSize != 0 {
		conn.Write([]byte("bad len\n"))
		return
	}
	plain, err := decrypt(sig, key)
	if err != nil {
		conn.Write([]byte("bad pad\n"))
		return
	}
	sigOk := verifySignature(plain, key)
	if !sigOk {
		conn.Write([]byte("bad sig\n"))
		return
	}
	conn.Write([]byte("what a nice signature you got there!\n"))
}

func initDataStore(d map[string][]byte, key []byte) {
	for _, c := range celebrities {
		v, err := encrypt(sign(c, key), key)
		if err != nil {
			continue
		}
		d[c] = v
	}
}

func run(conn net.Conn) {
	key := make([]byte, keyLength)
	rand.Read(key)
	dataStore := make(map[string][]byte, len(celebrities))
	initDataStore(dataStore, key)

	sample, err := encrypt(sign(the_flag, key), key)
	if err != nil {
		conn.Write([]byte("something went seriously wrong\n"))
		_ = conn.Close()
		return
	}
	defer conn.Close()
	sampleMessage := fmt.Sprintf("Here is a premium sample: %x\n", sample)
	conn.Write([]byte(sampleMessage))

	reader := bufio.NewReader(conn)
	menu := []byte(fmt.Sprint("What do you want to do?\n 1. Look at our free collection\n 2. Look at our premium collection\n 3. Verify a signature\n 4. Quit\n> "))
	for {
		_, err := conn.Write(menu)
		if err != nil {
			return
		}
		choice, err := reader.ReadString('\n')
		if err != nil {
			return
		}
		choice = strings.Trim(choice, " \t\r\n")
		if choice == "1" {
			freeCollection(dataStore, conn)
		} else if choice == "2" {
			premiumCollection(dataStore, key, reader, conn)
		} else if choice == "3" {
			verify(key, reader, conn)
		} else if choice == "4" {
			break
		} else {
			_, err := conn.Write([]byte("Enter 1, 2, 3 or 4\n"))
			if err != nil {
				return
			}
		}
	}
	conn.Write([]byte("Bye!\n"))
	//_ = conn.Close()
}

func main() {
	ln, err := net.Listen("tcp", "0.0.0.0:40011")
	if err != nil {
		fmt.Println("Could not listen")
		return
	}
	fmt.Println("Listener started")
	for {
		conn, err := ln.Accept()
		if err != nil {
			fmt.Println("encountered error when accepting...")
			continue
		}
		go run(conn)
	}
}
