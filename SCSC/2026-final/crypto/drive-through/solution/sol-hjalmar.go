package main

import (
	"bufio"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"net"
	"strconv"
	"strings"
)

func pad(origInput []byte, startL int) []byte {
	input := make([]byte, len(origInput), len(origInput)+72)
	copy(input, origInput)
	// length in bits
	L := len(input)*8 + startL
	// find K >= 0 s.t. (L+1+K+64) is multiple of 512
	K := (512 - ((L + 1 + 64) % 512)) % 512

	// Append '1'-bit, followed by K zeros
	input = append(input, byte(128))
	K -= 7
	for K > 0 {
		input = append(input, byte(0))
		K -= 8
	}

	if K != 0 {
		panic("bad K")
	}

	// Make room for 64 bit integer
	for i := 0; i < 8; i++ {
		input = append(input, byte(0))
	}
	// Add L
	binary.BigEndian.PutUint64(input[len(input)-8:], uint64(L))
	return input
}

func rightRotate(v, s uint32) uint32 {
	r := (v >> s) | (v << (32 - s))
	return r
}

// Based upon Wikipedia: https://en.wikipedia.org/wiki/SHA-2#Pseudocode
func doSha256(originalInput []byte, initial []uint32, startL int) []byte {
	unpaddedInput := make([]byte, len(originalInput), len(originalInput)+72)
	copy(unpaddedInput, originalInput)
	/*
	   Note 1: All variables are 32 bit unsigned integers and addition is calculated modulo 232
	   Note 2: For each round, there is one round constant k[i] and one entry in the message schedule array w[i], 0 ≤ i ≤ 63
	   Note 3: The compression function uses 8 working variables, a through h
	   Note 4: Big-endian convention is used when expressing the constants in this pseudocode,
	       and when parsing message block data from bytes to words, for example,
	       the first word of the input message "abc" after padding is 0x61626380
	*/

	/*
	   Initialize hash values:
	   (first 32 bits of the fractional parts of the square roots of the first 8 primes 2..19):
	*/
	h0 := uint32(0x6a09e667)
	h1 := uint32(0xbb67ae85)
	h2 := uint32(0x3c6ef372)
	h3 := uint32(0xa54ff53a)
	h4 := uint32(0x510e527f)
	h5 := uint32(0x9b05688c)
	h6 := uint32(0x1f83d9ab)
	h7 := uint32(0x5be0cd19)
	if initial != nil && len(initial) == 8 {
		h0 = initial[0]
		h1 = initial[1]
		h2 = initial[2]
		h3 = initial[3]
		h4 = initial[4]
		h5 = initial[5]
		h6 = initial[6]
		h7 = initial[7]
	}

	/*
	   Initialize array of round constants:
	   (first 32 bits of the fractional parts of the cube roots of the first 64 primes 2..311):
	*/
	var k = []uint32{0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2}

	/*
	   Pre-processing (Padding):
	   begin with the original message of length L bits
	   append a single '1' bit
	   append K '0' bits, where K is the minimum number >= 0 such that (L + 1 + K + 64) is a multiple of 512
	   append L as a 64-bit big-endian integer, making the total post-processed length a multiple of 512 bits
	   such that the bits in the message are: <original message of length L> 1 <K zeros> <L as 64 bit integer> , (the number of bits will be a multiple of 512)
	*/

	input := pad(unpaddedInput, startL)

	/*
	   Process the message in successive 512-bit chunks:
	   break message into 512-bit chunks
	*/
	w := make([]uint32, 64)
	for chunkIdx := 0; chunkIdx < len(input)*8/512; chunkIdx++ {
		/*
		   create a 64-entry message schedule array w[0..63] of 32-bit words
		   (The initial values in w[0..63] don't matter, so many implementations zero them here)
		   copy chunk into first 16 words w[0..15] of the message schedule array
		*/
		for j := 0; j < 16; j++ {
			i := j*4 + chunkIdx*512/8
			// big
			//w[j] = (uint32(input[i]) << 24) | (uint32(input[i+1]) << 16) | (uint32(input[i+2]) << 8) | (uint32(input[i+3]) << 0)
			// small
			//w[j] = (uint32(input[i]) << 0) | (uint32(input[i+1]) << 8) | (uint32(input[i+2]) << 16) | (uint32(input[i+3]) << 24)
			w[j] = binary.BigEndian.Uint32(input[i:])
		}

		//Extend the first 16 words into the remaining 48 words w[16..63] of the message schedule array:
		for i := 16; i < 64; i++ {
			s0 := rightRotate(w[i-15], 7) ^ rightRotate(w[i-15], 18) ^ (w[i-15] >> 3)
			s1 := rightRotate(w[i-2], 17) ^ rightRotate(w[i-2], 19) ^ (w[i-2] >> 10)
			w[i] = w[i-16] + s0 + w[i-7] + s1
		}

		// Initialize working variables to current hash value:
		a := h0
		b := h1
		c := h2
		d := h3
		e := h4
		f := h5
		g := h6
		h := h7

		//Compression function main loop:
		for i := 0; i < 64; i++ {
			S1 := rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)
			ch := (e & f) ^ ((^e) & g)
			temp1 := h + S1 + ch + k[i] + w[i]
			S0 := rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)
			maj := (a & b) ^ (a & c) ^ (b & c)
			temp2 := S0 + maj

			h = g
			g = f
			f = e
			e = d + temp1
			d = c
			c = b
			b = a
			a = temp1 + temp2
		}

		//Add the compressed chunk to the current hash value:
		h0 += a
		h1 += b
		h2 += c
		h3 += d
		h4 += e
		h5 += f
		h6 += g
		h7 += h
	}

	//Produce the final hash value (big-endian):
	ret := make([]byte, sha256.Size)
	binary.BigEndian.PutUint32(ret[0*4:], h0)
	binary.BigEndian.PutUint32(ret[1*4:], h1)
	binary.BigEndian.PutUint32(ret[2*4:], h2)
	binary.BigEndian.PutUint32(ret[3*4:], h3)
	binary.BigEndian.PutUint32(ret[4*4:], h4)
	binary.BigEndian.PutUint32(ret[5*4:], h5)
	binary.BigEndian.PutUint32(ret[6*4:], h6)
	binary.BigEndian.PutUint32(ret[7*4:], h7)
	//h0 append h1 append h2 append h3 append h4 append h5 append h6 append h7
	return ret
}

func extend(secretLength int, lastByte byte, originalOrder string, receipt []byte) ([]byte, []byte) {
	// Now we want to append to the message
	// We have
	// secret || "drink,snack" || pad
	// and the signature thereof
	// What we want is
	// secret || "drink,snack" || pad || ",flag" || pad

	paddedOrig := pad([]byte(originalOrder), secretLength*8)
	startL := (secretLength + len(paddedOrig)) * 8

	init := make([]uint32, 8)
	init[0] = binary.BigEndian.Uint32(receipt[0*4:])
	init[1] = binary.BigEndian.Uint32(receipt[1*4:])
	init[2] = binary.BigEndian.Uint32(receipt[2*4:])
	init[3] = binary.BigEndian.Uint32(receipt[3*4:])
	init[4] = binary.BigEndian.Uint32(receipt[4*4:])
	init[5] = binary.BigEndian.Uint32(receipt[5*4:])
	init[6] = binary.BigEndian.Uint32(receipt[6*4:])
	var lastRegister = [4]byte{receipt[28], receipt[29], receipt[30], lastByte}
	init[7] = binary.BigEndian.Uint32(lastRegister[:])
	secondPart := []byte(",flag")
	finalHash := doSha256(secondPart, init, startL)

	// Cut off last byte
	retHash := finalHash[:31]

	return append(paddedOrig, secondPart...), retHash
}

func main() {
	conn, err := net.Dial("tcp", "drive-through.ctf.wales:40013")
	if err != nil {
		fmt.Println("failed to connect")
		fmt.Println(err)
		return
	}
	// Place an order
	reader := bufio.NewReader(conn)
	_, err = reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to read greeting")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	// Choose option 1, then order "drink,snack"
	conn.Write([]byte("1\n"))
	_, err = reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to read question")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	conn.Write([]byte("drink,snack\n"))
	polynomial, err := reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to read polynomial")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	// Extract polynomial coeff
	eqInd := strings.Index(polynomial, "=")
	var coeff [3]int
	coeff[0], err = strconv.Atoi(string(polynomial[eqInd+1]))
	if err != nil {
		fmt.Println("could not parse coeff[0]")
	}
	coeff[1], err = strconv.Atoi(string(polynomial[eqInd+9]))
	if err != nil {
		fmt.Println("could not parse coeff[1]")
	}
	coeff[2], err = strconv.Atoi(string(polynomial[eqInd+15]))
	if err != nil {
		fmt.Println("could not parse coeff[2]")
	}
	x, err := strconv.Atoi(polynomial[eqInd+22 : strings.Index(polynomial, "\n")])
	if err != nil {
		fmt.Println("could not parse x")
	}
	// Send answer
	eval := fmt.Sprintf("%d\n", x*x*coeff[0]+x*coeff[1]+coeff[2])
	conn.Write([]byte(eval))

	// Collect order and receipt
	orderLine, err := reader.ReadString('\n')
	if err != nil {
		fmt.Println("failed to read order")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	if strings.Contains(orderLine, "declined") {
		fmt.Println("failed at polynomial")
		fmt.Print(polynomial)
		fmt.Println(coeff[0], coeff[1], coeff[2], x)
		fmt.Println(eval)
		_ = conn.Close()
		return
	}
	orderLine = strings.Trim(orderLine, " \t\r\n")
	order := orderLine[strings.Index(orderLine, ":")+2:]
	//fmt.Println("got order", order)

	receiptLine, err := reader.ReadString('\n')
	if err != nil {
		fmt.Println("failed to read receipt")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	receiptLine = strings.Trim(receiptLine, " \t\r\n")
	receiptText := receiptLine[strings.Index(receiptLine, ":")+2:]
	receipt, err := hex.DecodeString(receiptText)
	if err != nil {
		fmt.Println("failed to read hex")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	//fmt.Printf("got receipt %x\n", receipt)

	//runs := 0
	// Try all possible values for the last byte
	for b := 0; b < 256; b++ {
		// Try all possible values for the length of the secret
		for L := 16; L <= 32; L++ {
			//runs++
			mesg, h := extend(L, byte(b), order, receipt)
			_, err = reader.ReadString('>')
			if err != nil {
				fmt.Println("failed to reach menu")
				fmt.Println(err)
				_ = conn.Close()
				return
			}
			// Collect order
			conn.Write([]byte("2\n"))
			_, err = reader.ReadString('>')
			if err != nil {
				fmt.Println("failed to reach order prompt")
				fmt.Println(err)
				_ = conn.Close()
				return
			}
			conn.Write(mesg)
			conn.Write([]byte("\n"))
			_, err = reader.ReadString('>')
			if err != nil {
				fmt.Println("failed to reach receipt prompt")
				fmt.Println(err)
				_ = conn.Close()
				return
			}
			s := fmt.Sprintf("%x\n", h)
			conn.Write([]byte(s))

			// check result
			resp, err := reader.ReadString('\n')
			if err != nil {
				fmt.Println("failed to get answer from collect")
				fmt.Println(err)
				_ = conn.Close()
				return
			}
			if strings.Contains(resp, "Thank you") {
				// Success!
				s := strings.Index(resp, "SCSC{")
				e := strings.Index(resp, "}")
				fmt.Println(resp[s : e+1])
				b = 256
				L = 33
			}
		}
	}

	//fmt.Println("did", runs, "runs")

	_, _ = reader.ReadString('>')
	conn.Write([]byte("3\n"))
	_, _ = reader.ReadString('\n')
	_ = conn.Close()
}
