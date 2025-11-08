package main

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"flag"
	"fmt"
	"math/big"
	"os"
	"time"
)

func main() {
	certPath := flag.String("certpath", "ca_cert.pem", "Path to save the CA certificate")
	keyPath := flag.String("keypath", "ca_key.pem", "Path to save the CA private key")
	flag.Parse()

	// Generate a new private key using P-224 curve
	privKey, err := ecdsa.GenerateKey(elliptic.P224(), rand.Reader)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to generate private key: %v\n", err)
		os.Exit(1)
	}

	// Create a CA certificate template
	now := time.Now()
	sn, err := rand.Int(rand.Reader, new(big.Int).Lsh(big.NewInt(1), 128))
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
	certDER, err := x509.CreateCertificate(rand.Reader, &certTemplate, &certTemplate, &privKey.PublicKey, privKey)
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
