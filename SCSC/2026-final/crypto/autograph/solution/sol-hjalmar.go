package main

import (
	"bufio"
	"crypto/aes"
	"encoding/hex"
	"fmt"
	"net"
	"strings"
)

const keyLength = 32

// choose option 3, then send C, then parse answer.
// returns:
//
//	0: accepted
//	1: bad pad
//	2: bad sig
//	3: something else
func verify(C []byte, conn net.Conn, reader *bufio.Reader) int {
	conn.Write([]byte("3\n"))
	ans, err := reader.ReadString('>')
	if err != nil {
		return 3
	}
	conn.Write([]byte(hex.EncodeToString(C)))
	conn.Write([]byte("\n"))
	ans, err = reader.ReadString('>')
	if err != nil {
		return 3
	}
	if strings.Index(ans, "nice signature") >= 0 {
		return 0
	}
	if strings.Index(ans, "bad pad") >= 0 {
		return 1
	}
	if strings.Index(ans, "bad sig") >= 0 {
		return 2
	}
	return 3
}

func attack() {
	conn, err := net.Dial("tcp", "autograph.ctf.wales:40011")
	if err != nil {
		fmt.Println("failed to connect")
		return
	}
	reader := bufio.NewReader(conn)
	greeting, err := reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to read first greeting")
		_ = conn.Close()
		return
	}

	// extract free sample
	startDelim := "sample: "
	endDelim := "\n"
	indStart := strings.Index(greeting, startDelim) + len(startDelim)
	indEnd := strings.Index(greeting, endDelim)
	sampleStr := greeting[indStart:indEnd]
	sample, err := hex.DecodeString(sampleStr)

	//fmt.Printf("got sample: %x\n", sample)

	// Start by trying to find the padding length
	C := make([]byte, len(sample))
	P := make([]byte, len(sample))
	copy(P, sample)
	copy(C, sample)
	numBlocks := len(sample) / aes.BlockSize
	numPadding := -1
	// Flip last byte in second to last block, second last byte, ...
	for bPos := aes.BlockSize - 1; bPos >= 0; bPos-- {
		C[(numBlocks-2)*aes.BlockSize+bPos] = ^C[(numBlocks-2)*aes.BlockSize+bPos]
		status := verify(C, conn, reader)
		if status == 3 {
			fmt.Println("something bad happened, leaving")
			conn.Write([]byte("4\n"))
			_ = conn.Close()
		}
		if status == 2 { // pad sig means we got through the padding verification
			// Got correct padding
			numPadding = aes.BlockSize - bPos - 1
		}
		C[(numBlocks-2)*aes.BlockSize+bPos] = ^C[(numBlocks-2)*aes.BlockSize+bPos]
		if numPadding > -1 {
			break
		}
	}

	if numPadding < 0 {
		//fmt.Println("unexpected padding length, setting to 0")
		numPadding = 0
	}
	//fmt.Println("there are", numPadding, "bytes of padding")
	for i := len(P) - numPadding; i < len(P); i++ {
		P[i] = byte(numPadding)
	}
	byteValue := numPadding
	bPos := aes.BlockSize - 1 - numPadding
	for cidx := numBlocks - 2; cidx >= 0; cidx-- {
		//fmt.Println("working on cipher block", cidx)
		pidx := cidx + 1
		for ; bPos >= 0; bPos-- {
			for i := len(C) - aes.BlockSize - byteValue; i < len(C)-aes.BlockSize; i++ {
				C[i] ^= byte(byteValue ^ (byteValue + 1))
			}
			for bVal := 0; bVal <= 255; bVal++ {
				C[cidx*aes.BlockSize+bPos] = byte(bVal)

				status := verify(C, conn, reader)
				if status <= 1 { // success or pad pad
					// success is highly unlikely
					continue
				} else if status == 2 { // pad sig
					P[pidx*aes.BlockSize+bPos] = byte(bVal^(byteValue+1)) ^ sample[cidx*aes.BlockSize+bPos]
					break
				} else { // bad error
					fmt.Println("bPos =", bPos, "fatal")
					conn.Write([]byte("4\n"))
					_ = conn.Close()
					return
				}
			}
			byteValue++
		}
		// Cut off end of C
		C = C[:len(C)-aes.BlockSize]
		copy(C, sample)
		byteValue = 0
		bPos = aes.BlockSize - 1
	}
	// Remove IV
	P = P[aes.BlockSize:]
	//fmt.Printf("recovered plaintext and signature %x\n", P)
	// Remove trailing HMAC and padding
	P = P[:len(P)-keyLength-numPadding]
	fmt.Println(string(P))

	conn.Write([]byte("4\n"))
	_ = conn.Close()
}

func main() {
	attack()
}
