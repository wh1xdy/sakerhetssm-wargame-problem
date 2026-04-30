package main

import (
	"bufio"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"fmt"
	"math/big"
	"net"
	"strconv"
	"strings"
)

var menu = map[string]string{
	"drink":   "pepsi",
	"snack":   "halkidiki-olives",
	"dessert": "pralines",
	"fruit":   "banana",
	"flag":    the_flag,
}

func signReceipt(order string, secret []byte) []byte {
	h := sha256.Sum256(append(secret, []byte(order)...))
	// Cut off the last byte
	ret := make([]byte, sha256.Size-1)
	copy(ret, h[:])
	return ret
}

func randomPolynomial() []int {
	ret := make([]int, 4)
	for i := 0; i < 3; i++ {
		j, _ := rand.Int(rand.Reader, big.NewInt(7))
		ret[i] = 2 + int(j.Int64())
	}
	j, _ := rand.Int(rand.Reader, big.NewInt(6))
	ret[3] = int(j.Int64()) - 2
	return ret
}

func orderFromMenu(secret []byte, reader *bufio.Reader, conn net.Conn) {
	conn.Write([]byte("Please enter your choice. Order multiple items by separating them with commas\n"))
	for k, _ := range menu {
		s := fmt.Sprintf(" %s\n", k)
		conn.Write([]byte(s))
	}
	conn.Write([]byte(" > "))
	choice, err := reader.ReadString('\n')
	if err != nil {
		conn.Write([]byte("bad choice\n"))
		return
	}
	choice = strings.ToLower(strings.Trim(choice, " \t\r\n"))
	if strings.Contains(choice, "flag") {
		conn.Write([]byte("sorry, we are all out of that\n"))
		return
	}
	splitChoices := strings.Split(choice, ",")
	ret := make([]string, 0, len(splitChoices))
	for _, c := range splitChoices {
		ct := strings.Trim(c, " \t")
		_, ok := menu[ct]
		if ok {
			ret = append(ret, ct)
		}
	}
	if len(ret) == 0 {
		conn.Write([]byte("you don't want anything?\n"))
		return
	}

	coeff := randomPolynomial()
	correct := coeff[0]*coeff[3]*coeff[3] + coeff[1]*coeff[3] + coeff[2]

	for {
		s := fmt.Sprintf("Payment please! Evaluate p(x)=%d*x^2 + %d*x + %d at x=%d\n > ", coeff[0], coeff[1], coeff[2], coeff[3])
		conn.Write([]byte(s))
		answer, err := reader.ReadString('\n')
		if err != nil {
			conn.Write([]byte("bad answer\n"))
			return
		}
		answer = strings.Trim(answer, " \t\r\n")
		theirAnswer, err := strconv.Atoi(answer)
		if err != nil {
			conn.Write([]byte("a number please\n"))
			continue
		}
		if theirAnswer == correct {
			break
		} else {
			conn.Write([]byte("uhhh, your card declined... try another one?\n"))
		}
	}

	order := strings.Join(ret, ",")
	receipt := signReceipt(order, secret)
	toSend := fmt.Sprintf("here you go: %s\nhere is a signed receipt: %x\nCollect your order at the next window\n", order, receipt)
	conn.Write([]byte(toSend))
	return
}

func collectOrder(secret []byte, reader *bufio.Reader, conn net.Conn) {
	conn.Write([]byte("Hello! Please tell me your order and show your receipt\n"))
	conn.Write([]byte(" order > "))
	order, err := reader.ReadString('\n')
	if err != nil {
		conn.Write([]byte("bad order\n"))
		return
	}
	order = strings.Trim(order, " \t\r\n")
	conn.Write([]byte(" receipt > "))
	receipt, err := reader.ReadString('\n')
	if err != nil {
		conn.Write([]byte("bad receipt\n"))
		return
	}
	receipt = strings.Trim(receipt, " \t\r\n")
	userReceipt, err := hex.DecodeString(receipt)
	if err != nil {
		conn.Write([]byte("bad hex\n"))
		return
	}
	validateReceipt := signReceipt(order, secret)
	if subtle.ConstantTimeCompare(validateReceipt, userReceipt) != 1 {
		conn.Write([]byte("that receipt is forged!\n"))
		return
	}

	ret := make([]string, 0)
	orderedItems := strings.Split(order, ",")
	for _, o := range orderedItems {
		v, ok := menu[strings.Trim(o, " ")]
		if ok {
			ret = append(ret, v)
		}
	}
	if len(ret) == 0 {
		conn.Write([]byte("you didn't order anything?\n"))
		return
	}
	s := fmt.Sprintf("Thank you for using the drive-through: %s\n", strings.Join(ret, ","))
	conn.Write([]byte(s))
}

func run(conn net.Conn) {
	reader := bufio.NewReader(conn)
	// Pick a random length from [16,32]
	randValue, err := rand.Int(rand.Reader, big.NewInt(17))
	if err != nil {
		conn.Write([]byte("Something went seriously wrong, exiting\n"))
		_ = conn.Close()
		return
	}
	secretLength := int(randValue.Int64()) + 16
	secret := make([]byte, secretLength)
	rand.Read(secret)

	for {
		conn.Write([]byte("Welcome to the drive through! What do you want to do?\n 1. Order from the menu\n 2. Collect your order\n 3. Quit\n > "))
		choice, err := reader.ReadString('\n')
		if err != nil {
			conn.Write([]byte("bad choice\n"))
			break
		}
		choice = strings.Trim(choice, " \t\r\n")
		if choice == "1" {
			orderFromMenu(secret, reader, conn)
		} else if choice == "2" {
			collectOrder(secret, reader, conn)
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
	ln, err := net.Listen("tcp", "0.0.0.0:40013")
	if err != nil {
		fmt.Println("failed to start listener")
		fmt.Println(err)
		return
	}
	fmt.Println("Listener started")
	for {
		conn, err := ln.Accept()
		if err != nil {
			fmt.Println("failed to accept")
			fmt.Println(err)
			continue
		}
		go run(conn)
	}
}
