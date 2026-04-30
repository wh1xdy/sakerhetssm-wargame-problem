package main

import (
	"bufio"
	"crypto/rand"
	"fmt"
	"math/big"
	"math/bits"
	"net"
	"strings"
)

type randomState struct {
	last [8]uint64
}

func (r *randomState) shake(n uint64) uint64 {
	for i := 0; i < 7; i++ {
		v := r.last[i]
		w := r.last[i+1]
		if i&1 == 1 {
			n ^= v >> (w & 15)
		} else {
			n ^= v << (w & 7)
		}
		r.last[i] = w
	}
	r.last[7] = n
	return n
}

func (r *randomState) nextRandom() uint64 {
	s := r.last[7]
	mix := r.shake(s)
	return mix
}

func sign(s uint64) uint64 {
	hi, lo := bits.Mul64(s+0xa0761d6478bd642f, s^0xe7037ed1a0b428db)
	return hi ^ lo
}

// This is sooooo slow...
func createRandomState() *randomState {
	state := new(randomState)
	for i := 0; i < 8; i++ {
		seed, err := rand.Int(rand.Reader, new(big.Int).Lsh(big.NewInt(1), 64))
		if err != nil {
			fmt.Print("something went wrong...\n")
		}
		state.last[i] = seed.Uint64()
	}
	return state
}

func run(conn net.Conn) {
	reader := bufio.NewReader(conn)
	randomState := createRandomState()
	// ensure that we don't get all zeros again
	conn.Write([]byte(fmt.Sprintf("DEBUG init: %d\n", randomState.nextRandom())))
	maxTries := 5
	for i := 0; i < maxTries; i++ {
		try := "tries"
		if i == maxTries-1 {
			try = "try"
		}
		toSend := fmt.Sprintf("%d %s remaining!\n", maxTries-i, try)
		conn.Write([]byte(toSend))
		// much faster
		r := randomState.nextRandom()
		rStr := fmt.Sprintf("Guess what the signature of this will be (in base 10): %d\n > ", r)
		conn.Write([]byte(rStr))
		inp, err := reader.ReadString('\n')
		if err != nil {
			conn.Write([]byte("failed to read\n"))
			break
		}
		inp = strings.Trim(inp, " \t\r\n")
		guess, ok := new(big.Int).SetString(inp, 10)
		if !ok {
			conn.Write([]byte("bad number, enter in base 10\n"))
			break
		}
		s := randomState.nextRandom()
		// add salt
		signature := sign(r + s)
		if signature == guess.Uint64() {
			conn.Write([]byte(fmt.Sprintf("Good job! Here you go: %s\n", theFlag)))
			break
		} else {
			conn.Write([]byte("Nope!\n"))
		}
	}
	conn.Write([]byte("Bye!\n"))
	_ = conn.Close()
}

func main() {
	ln, err := net.Listen("tcp", "0.0.0.0:40123")
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
