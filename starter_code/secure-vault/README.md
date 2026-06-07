# Secure Crypto Vault (Python)

A professional-grade CLI utility demonstrating industry-standard security implementations for credential management.

## Features
- **Authenticated Encryption:** Uses AES-256-GCM (Galois/Counter Mode) for both confidentiality and integrity.
- **Secure Key Derivation:** Implements PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP recommendation).
- **Master Password Protection:** Uses the `getpass` module to mask password entry.
- **Persistent Storage:** Encrypted credentials are saved to a local `vault.json` file.

## Setup Instructions
1. Navigate to the project folder:
   ```bash
   cd starter_code/secure-vault

2. **Install the required security library:**
   ```bash
   pip install -r requirements.txt

3. **Run the application:**
   ```bash
   python vault.py         

## Security Implementation Details
This project prioritizes high-entropy security and follows modern cryptographic standards:

- **Key Derivation (PBKDF2):**
  - **Algorithm:** HMAC-SHA256
  - **Iterations:** 600,000 (Aligned with OWASP 2024 password storage recommendations).
  - **Salt:** 16-byte cryptographically secure random salt generated via `os.urandom()`.
  
- **Authenticated Encryption (AES-GCM):**
  - **Mode:** AES-256-GCM (Galois/Counter Mode).
  - **Integrity:** Unlike standard AES-CBC, GCM provides built-in authentication, ensuring that the ciphertext has not been tampered with.
  - **Nonce:** A unique 12-byte initialization vector (IV) is generated for every individual entry.

- **Storage:**
  - Sensitive data is never stored in plain text.
  - The `vault.json` file contains only the Salt, Nonce, and Ciphertext in hexadecimal format.