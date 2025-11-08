package main

import (
	"bytes"
	"crypto/tls"
	"crypto/x509"
	"flag"
	"fmt"
	"net/http"
	"os"
	"strings"
)

func loadCA(certPath string) (*x509.CertPool, error) {
	certData, err := os.ReadFile(certPath)
	if err != nil {
		return nil, err
	}

	certPool := x509.NewCertPool()
	if !certPool.AppendCertsFromPEM(certData) {
		return nil, fmt.Errorf("failed to append CA certificate")
	}

	return certPool, nil
}

var caCertPath = flag.String("cacert", "cert.pem", "Path to CA certificate")
var flagPath = flag.String("flagpath", "flag.txt", "Path to the flag")

func main() {
	flag.Parse()
	fmt.Println("What URL do you want the flag to?")
	var url string
	if _, err := fmt.Scanln(&url); err != nil {
		fmt.Fprintf(os.Stderr, "Failed reading url: %v\n", err)
		os.Exit(1)
	}

	if !strings.HasPrefix(url, "https://") {
		fmt.Fprintf(os.Stderr, "URL does not start with \"https://\"\n")
		os.Exit(1)
	}

	// Load the CA certificate
	certPool, err := loadCA(*caCertPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to load CA certificate: %v\n", err)
		os.Exit(1)
	}

	// Configure TLS with the CA certificate
	client := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{
				RootCAs: certPool,
			},
		},
	}

	// Sample JSON payload
	data, err := os.ReadFile(*flagPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed reading flag: %v\n", err)
		os.Exit(1)
	}
	jsonData := []byte(fmt.Sprintf(`{"flag": "%s"}`, strings.TrimSpace(string(data))))

	if _, err := client.Post(url, "application/json", bytes.NewBuffer(jsonData)); err != nil {
		fmt.Fprintf(os.Stderr, "Request failed: %v\n", err)
		os.Exit(1)
	}
}
