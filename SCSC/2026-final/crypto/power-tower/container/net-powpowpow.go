package main

import (
	"bufio"
	"crypto/rand"
	"fmt"
	"math/big"
	"net"
	"strings"
)

const super_secret_admin_password = "yes it is me the super important and secure admin with full privileges"

func init_random() (*big.Int, *big.Int, *big.Int, *big.Int) {
	var p, q, N, S, e, d, seed *big.Int
	var err error
	for {
		p, err = rand.Prime(rand.Reader, 1024)
		if err == nil {
			break
		}
	}
	for {
		q, err = rand.Prime(rand.Reader, 1024)
		if err == nil {
			break
		}
	}
	for {
		seed, err = rand.Prime(rand.Reader, 1024)
		if err == nil {
			break
		}
	}
	N = new(big.Int).Mul(p, q)
	p.Sub(p, big.NewInt(1))
	q.Sub(q, big.NewInt(1))
	S = new(big.Int).Mul(p, q)
	e = big.NewInt(65537)
	d = new(big.Int).ModInverse(e, S)
	return e, d, N, seed
}

func power_encrypt(e, d, N, m, seed *big.Int) *big.Int {
	res := new(big.Int).Mod(seed, N)
	mask := big.NewInt(0xffff)
	localm := new(big.Int).Set(m)
	v := big.NewInt(0)
	for localm.Sign() == 1 {
		v.And(localm, mask)
		res.Exp(res, v, N)
		localm.Rsh(localm, 16)
	}
	res.Exp(res, e, N)
	return res
}

func enter_power_tower(e, d, N, seed *big.Int, conn net.Conn, reader *bufio.Reader) {
	question := []byte("Please enter you message to the power tower > ")
	_, err := conn.Write(question)
	if err != nil {
		return
	}
	message, err := reader.ReadString('\n')
	if err != nil {
		return
	}
	message = strings.Trim(message, " \r\n\t")
	if len(message) < 16 {
		conn.Write([]byte("We only accept loooooong messages (we are very secure!)\n"))
		return
	}
	if message == super_secret_admin_password {
		conn.Write([]byte("No no no, don't even try!\n"))
		return
	}
	messagebytes := []byte(message)
	m := new(big.Int).SetBytes(messagebytes)
	res := power_encrypt(e, d, N, m, seed)
	tosend := fmt.Sprintf("Here is the output: %s\n", res)
	_, _ = conn.Write([]byte(tosend))
}

func enter_admin_panel(e, d, N, admin_password *big.Int, conn net.Conn, reader *bufio.Reader) {
	_, err := conn.Write([]byte("Please enter admin password > "))
	if err != nil {
		return
	}
	password, err := reader.ReadString('\n')
	if err != nil {
		return
	}
	password = strings.Trim(password, " \r\n\t")
	m, success := new(big.Int).SetString(password, 10)

	if !success {
		_, _ = conn.Write([]byte("Enter number in base 10\n"))
		return
	}
	if m.Cmp(admin_password) == 0 {
		_, _ = conn.Write([]byte("Here is the flag: "))
		_, _ = conn.Write([]byte(flag))
		_, _ = conn.Write([]byte("\n"))
	} else {
		_, _ = conn.Write([]byte("Nope!\n"))
	}

}

func run(conn net.Conn) {
	reader := bufio.NewReader(conn)
	e, d, N, seed := init_random()
	m := new(big.Int).SetBytes([]byte(super_secret_admin_password))
	admin_password := power_encrypt(e, d, N, m, seed)

	greeting := fmt.Sprintf("The super secret password is:\n\t%s\nN = %s\n\n", super_secret_admin_password, N)
	_, err := conn.Write([]byte(greeting))
	if err != nil {
		// Failed to write
		_ = conn.Close()
		return
	}

	question := []byte("What do you want to do?\n\t1: Build a PowerTower\n\t2: Enter admin panel\n\t3: Quit\n> ")
	var choice string
	for {
		_, err = conn.Write(question)
		if err != nil {
			break
		}
		choice, err = reader.ReadString('\n')
		if err != nil {
			break
		}
		choice = strings.Trim(choice, " \r\n\t")
		if choice == "1" {
			enter_power_tower(e, d, N, seed, conn, reader)
		} else if choice == "2" {
			enter_admin_panel(e, d, N, admin_password, conn, reader)
		} else if choice == "3" {
			break
		} else {
			conn.Write([]byte("Enter 1, 2 or 3\n"))
		}
	}
	conn.Write([]byte("Bye!\n"))
	_ = conn.Close()
}

func main() {
	ln, err := net.Listen("tcp", "0.0.0.0:40010")
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
