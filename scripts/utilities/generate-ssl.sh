#!/bin/bash

# NEXUS Platform - SSL Certificate Generation Script
# Generates self-signed certificates for development/testing

set -e

SSL_DIR="ssl"
CERT_NAME="nexus"
DOMAIN="localhost"

echo "🔐 Generating SSL certificates for NEXUS Platform..."

# Create SSL directory
mkdir -p $SSL_DIR

# Generate private key
echo "📝 Generating private key..."
openssl genrsa -out $SSL_DIR/$CERT_NAME.key 2048

# Generate certificate signing request
echo "📝 Generating certificate signing request..."
openssl req -new -key $SSL_DIR/$CERT_NAME.key -out $SSL_DIR/$CERT_NAME.csr -subj "/C=US/ST=CA/L=San Francisco/O=NEXUS Platform/OU=IT Department/CN=$DOMAIN"

# Generate self-signed certificate
echo "📝 Generating self-signed certificate..."
openssl x509 -req -days 365 -in $SSL_DIR/$CERT_NAME.csr -signkey $SSL_DIR/$CERT_NAME.key -out $SSL_DIR/$CERT_NAME.crt

# Generate DH parameters
echo "📝 Generating DH parameters..."
openssl dhparam -out $SSL_DIR/dhparam.pem 2048

# Set proper permissions
chmod 600 $SSL_DIR/$CERT_NAME.key
chmod 644 $SSL_DIR/$CERT_NAME.crt
chmod 644 $SSL_DIR/dhparam.pem

echo "✅ SSL certificates generated successfully!"
echo "📁 Certificate files:"
echo "   - Private Key: $SSL_DIR/$CERT_NAME.key"
echo "   - Certificate: $SSL_DIR/$CERT_NAME.crt"
echo "   - DH Parameters: $SSL_DIR/dhparam.pem"

echo ""
echo "🔧 To use these certificates:"
echo "1. Update nginx configuration to use the certificates"
echo "2. Restart nginx container"
echo "3. Access via https://localhost"

# Verify certificates
echo ""
echo "🔍 Verifying certificates..."
openssl x509 -in $SSL_DIR/$CERT_NAME.crt -text -noout | grep -E "(Subject:|Not Before|Not After)"
