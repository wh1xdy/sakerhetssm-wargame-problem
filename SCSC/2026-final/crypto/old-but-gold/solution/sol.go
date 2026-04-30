package main

import (
	"bufio"
	"fmt"
	"math/bits"
	"net"
	"strconv"
	"strings"
)

func sign(s uint64) uint64 {
	hi, lo := bits.Mul64(s+0xa0761d6478bd642f, s^0xe7037ed1a0b428db)
	return hi ^ lo
}

func attack() bool {
	conn, err := net.Dial("tcp", "old-but-gold.ctf.wales:40123")
	if err != nil {
		fmt.Println("failed to connect")
		return false
	}
	reader := bufio.NewReader(conn)
	greeting, err := reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to read first greeting")
		_ = conn.Close()
		return false
	}

	// extract debug init
	startDelim := "DEBUG init: "
	endDelim := "\n"
	indStart := strings.Index(greeting, startDelim) + len(startDelim)
	indEnd := strings.Index(greeting, endDelim)
	sampleStr := greeting[indStart:indEnd]
	sample, err := strconv.ParseUint(sampleStr, 10, 64)
	if err != nil {
		fmt.Println("failed to parse sample")
		fmt.Println(err)
		return false
	}

	startDelim = "base 10): "
	endDelim = "\n >"
	indStart = strings.Index(greeting, startDelim) + len(startDelim)
	indEnd = strings.Index(greeting, endDelim)
	BStr := greeting[indStart:indEnd]
	B, err := strconv.ParseUint(BStr, 10, 64)
	if err != nil {
		fmt.Println("failed to parse B")
		fmt.Println(err)
		return false
	}

	for i := 0; i < 3; i++ {
		conn.Write([]byte("0\n"))
		_, err = reader.ReadString('>')
		if err != nil {
			fmt.Println("failed to query")
			_ = conn.Close()
			return false
		}
	}

	conn.Write([]byte("0\n"))
	final, err := reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to get final")
		_ = conn.Close()
		return false
	}

	indStart = strings.Index(final, startDelim) + len(startDelim)
	indEnd = strings.Index(final, endDelim)
	finalStr := final[indStart:indEnd]
	fin, err := strconv.ParseUint(finalStr, 10, 64)
	if err != nil {
		fmt.Println("failed to parse sample")
		fmt.Println(err)
		return false
	}

	s := sample << (B & 7)
	s ^= B ^ fin
	sig := sign(fin + s)
	conn.Write([]byte(fmt.Sprintf("%d\n", sig)))

	res := ""
	for {
		r, err := reader.ReadString('\n')
		if err != nil {
			fmt.Println("failed to get res")
			_ = conn.Close()
			return false
		}
		if strings.Contains(r, "Bye!") {
			break
		}
		res = r
	}
	ret := false
	if strings.Contains(res, "Good job!") {
		s := strings.Index(res, "SCSC{")
		e := strings.Index(res, "}")
		fmt.Println(res[s : e+1])
		ret = true
	}

	_ = conn.Close()
	return ret
}

func main() {
	for {
		if attack() {
			break
		}
	}
}
