package main

import (
	"bufio"
	"fmt"
	"net"
	"strings"
)

func main() {
	conn, err := net.Dial("tcp", "127.0.0.1:50000")
	if err != nil {
		fmt.Println("failed to connect")
		fmt.Println(err)
		return
	}
	reader := bufio.NewReader(conn)
	_, err = reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to get to menu #1")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	// Send shuffled last pair of chars
	conn.Write([]byte("1\n"))
	_, err = reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to get to getting prompted for message")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	conn.Write([]byte("yes it is me the super important and secure admin with full privileseg\n"))
	hasPass, err := reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to get to menu #2")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	s := "is the output: "
	e := "\n"
	sIdx := strings.Index(hasPass, s)
	eIdx := strings.Index(hasPass, e)
	// get the "password"
	num := hasPass[sIdx+len(s) : eIdx+1]

	// send the password
	conn.Write([]byte("2\n"))
	_, err = reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to get to getting prompted for message")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	conn.Write([]byte(num))
	conn.Write([]byte("\n"))
	hasFlag, err := reader.ReadString('>')
	if err != nil {
		fmt.Println("failed to get to getting prompted for message")
		fmt.Println(err)
		_ = conn.Close()
		return
	}
	s = "SCSC{"
	e = "}"
	sIdx = strings.Index(hasFlag, s)
	eIdx = strings.Index(hasFlag, e)
	flag := hasFlag[sIdx : eIdx+1]
	fmt.Println(flag)

	// quit
	conn.Write([]byte("3\n"))
	_ = conn.Close()
}
