package main

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/hex"
	"encoding/pem"
	"flag"
	"fmt"
	"math/big"
	"os"
	"strings"
	"time"
)

// fixedReader implements io.Reader using a fixed byte stream from a file
type fixedReader struct {
	data []byte
	pos  int
}

func (r *fixedReader) Read(p []byte) (n int, err error) {
	if r.pos >= len(r.data) {
		return 0, fmt.Errorf("EOF")
	}
	n = copy(p, r.data[r.pos:])
	r.pos += n
	return n, nil
}

func newFixedReaderFromFile(path string) (*fixedReader, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	// Convert \xAB\xCD format into raw bytes
	hexString := strings.ReplaceAll(strings.TrimSpace(string(content)), "\\x", "")
	data, err := hex.DecodeString(hexString)
	if err != nil {
		return nil, err
	}

	return &fixedReader{data: data}, nil
}

func main() {
	certPath := flag.String("certpath", "ca_cert.pem", "Path to save the CA certificate")
	keyPath := flag.String("keypath", "ca_key.pem", "Path to save the CA private key")
	seedPath := flag.String("seedfile", "seed.txt", "Path to file containing the random byte stream")
	flag.Parse()

	// Load fixed reader
	reader, err := newFixedReaderFromFile(*seedPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read seed file: %v\n", err)
		os.Exit(1)
	}

	// Generate a new private key using P-224 curve
	privKey, err := ecdsa.GenerateKey(elliptic.P224(), reader)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to generate private key: %v\n", err)
		os.Exit(1)
	}

	// Create a CA certificate template
	now, err := time.Parse("2006-01-02 15:04:05", "2025-03-02 15:57:01")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to parse time: %v\n", err)
		os.Exit(1)
	}
	sn, err := rand.Int(reader, new(big.Int).Lsh(big.NewInt(1), 128))
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to generate serial number: %v\n", err)
		os.Exit(1)
	}

	certTemplate := x509.Certificate{
		SerialNumber:          sn,
		Subject:               pkix.Name{CommonName: "Certifiably Secure"},
		NotBefore:             now,
		NotAfter:              now.Add(10 * 365 * 24 * time.Hour), // 10 years validity
		KeyUsage:              x509.KeyUsageCertSign | x509.KeyUsageCRLSign,
		IsCA:                  true,
		BasicConstraintsValid: true,
	}

	// Create the CA certificate
	certDER, err := x509.CreateCertificate(reader, &certTemplate, &certTemplate, &privKey.PublicKey, privKey)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to create certificate: %v\n", err)
		os.Exit(1)
	}

	// Save the CA certificate to a file
	certFile, err := os.Create(*certPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open cert file: %v\n", err)
		os.Exit(1)
	}
	defer certFile.Close()

	if err := pem.Encode(certFile, &pem.Block{Type: "CERTIFICATE", Bytes: certDER}); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to write certificate: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Certificate saved to %s\n", *certPath)

	// Save the CA private key to a file
	keyFile, err := os.Create(*keyPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open key file: %v\n", err)
		os.Exit(1)
	}
	defer keyFile.Close()

	privKeyBytes, err := x509.MarshalECPrivateKey(privKey)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to marshal private key: %v\n", err)
		os.Exit(1)
	}

	if err := pem.Encode(keyFile, &pem.Block{Type: "EC PRIVATE KEY", Bytes: privKeyBytes}); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to write private key: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Private key saved to %s\n", *keyPath)
}
