"""
vault.py
===============
Project:    Secure Crypto Vault
Difficulty: Advanced
Category:   Cybersecurity & Cryptography
Skills:     Python, cryptography (AES-GCM), PBKDF2HMAC, JSON, getpass
Time:       Medium (a weekend)

What you will build:
    A high-security CLI vault to store service credentials (usernames/passwords). 
    It uses AES-256-GCM for encryption, PBKDF2 for key derivation to protect 
    against brute-force attacks, and stores data in an encrypted JSON format.

How to run:
    pip install cryptography
    python vault.py

Learning goals:
    - Implementing industry-standard AES-GCM encryption
    - Securing passwords using Key Derivation Functions (KDF)
    - Handling sensitive binary data as Hexadecimal strings in JSON
    - Managing session-based authentication without storing plain-text passwords

Roadmap:
    Step 1:  Install 'cryptography' and run the skeleton to verify the menu
    Step 2:  Complete derive_key() using PBKDF2HMAC with 600,000 iterations
    Step 3:  Implement vault setup: generate a salt and the initial 'test_lock'
    Step 4:  Implement vault login: verify the Master Password against the lock
    Step 5:  Complete 'Add Password': encrypt credentials with a unique nonce
    Step 6:  Complete 'Get Password': decrypt and split stored service data
    Step 7:  Implement the Audit feature to view raw encrypted Hex strings
    Step 8:  Test security by attempting to view vault.json contents manually
"""
        
import json
import os
import secrets
import sys
import getpass # This module allows us to hide the password as the user types it
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# This is the name of the file where all our encrypted data will live
VAULT_FILE = "vault.json"

def get_input(prompt):
    """
    A helper function to get text from the user.
    If the user types 'q', the program exits immediately.
    """
    user_input = input(prompt).strip()
    if user_input.lower() == 'q':
        print("\nExiting Secure Vault. Stay safe!")
        sys.exit()
    return user_input

def derive_key(password: str, salt: bytes) -> bytes:
    """
    This is a Key Derivation Function (KDF).
    It takes your easy-to-remember password and turns it into a 
    mathematically strong 32-byte key for the encryption algorithm.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000, # Running this 600k times makes it very slow for hackers to guess
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def save_vault(data):
    """Takes our Python dictionary and writes it into the JSON file."""
    with open(VAULT_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_vault():
    """Tries to open the vault file. Returns None if the file is missing or broken."""
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("[ERROR] Vault file corrupted or unreadable.")
            return None
    return None

def main():
    print("==============================")
    print("--- SECURE CRYPTO VAULT ---")
    print("(Type 'q' at any time to quit)")
    print("==============================")
    
    # Step 1: Try to load existing vault data
    vault = load_vault()
    
    if not vault:
        # If no vault exists, we start the setup process
        print("No vault detected. Let's set it up.")
        master_pw = ""
        while not master_pw.strip():
            # getpass.getpass hides the characters while typing for safety
            master_pw = getpass.getpass("Create a strong Master Password: ").strip()
            if master_pw.lower() == 'q': sys.exit()
            if not master_pw.strip():
                print("[ERROR] Master Password cannot be empty!")
        
        # Salt is random data mixed with the password to prevent pre-computed attacks
        salt = secrets.token_bytes(16)
        temp_key = derive_key(master_pw, salt)
        temp_aes = AESGCM(temp_key)
        
        # We create a 'test lock'. Later, if we can decrypt this, we know the password is correct.
        temp_nonce = secrets.token_bytes(12)
        test_lock = temp_aes.encrypt(temp_nonce, b"SUCCESS", None)

        # Prepare the dictionary that will be saved to vault.json
        vault = {
            "salt": salt.hex(), 
            "test_nonce": temp_nonce.hex(),
            "test_lock": test_lock.hex(),
            "entries": {}
        }
        save_vault(vault)
        print("[SUCCESS] Vault created successfully!")
        key = temp_key
    else:
        # If a vault exists, the user must log in
        master_pw = getpass.getpass("Enter Master Password: ").strip()
        if master_pw.lower() == 'q': sys.exit()
        
        # Load the saved salt and test data from the JSON
        salt = bytes.fromhex(vault["salt"])
        test_nonce = bytes.fromhex(vault["test_nonce"])
        test_lock = bytes.fromhex(vault["test_lock"])

        # Re-create the key from the entered password
        key = derive_key(master_pw, salt)
        aesgcm_test = AESGCM(key)
        
        try:
            # Try to unlock the test message. If this fails, an exception is triggered.
            aesgcm_test.decrypt(test_nonce, test_lock, None)
            print("[ACCESS GRANTED]")
        except Exception:
            print("\n[ALERT] INCORRECT MASTER PASSWORD!")
            print("TERMINATING SESSION FOR SECURITY.")
            return

    # Once logged in, we initialize our encryption engine (AES-GCM)
    aesgcm = AESGCM(key)

    while True:
        print("\n--- Main Menu ---")
        print("[1] List Services")
        print("[2] Exit")
        choice1 = get_input("Select an option: ")

        if not choice1:
            print("[WARN] Choice cannot be empty!")
            continue

        if choice1 == "1":
            while True:
                # Display the names of all services currently stored
                print("\n--- Registered Services ---")
                if not vault["entries"]:
                    print("(No services saved yet)")
                else:
                    # sorted() ensures 'Apple' comes before 'Zillow'
                    for s in sorted(vault["entries"].keys()):
                        print(f" - {s}")

                print("\n--- Service Options ---")
                print("[1] Add Password")
                print("[2] Get Password")
                print("[3] Display All Secrets")
                print("[4] Delete Entry")
                print("[5] Audit Metadata (View Raw JSON Storage)")
                print("[6] Back")
                choice2 = get_input("Select: ")

                if not choice2:
                    print("[WARN] Choice cannot be empty!")
                    continue

                if choice2 == "1":
                    # Option to encrypt and save a new set of credentials
                    service = ""
                    while not service.strip():
                        service = get_input("Service Name (e.g., Google, GitHub...): ").lower()
                        if not service: print("[ERROR] Service name cannot be empty!")
                    
                    username = ""
                    while not username.strip():
                        username = get_input("Username: ")
                        if not username: print("[ERROR] Username cannot be empty!")
                    
                    password = ""
                    while not password.strip():
                        password = get_input("Password: ")
                        if not password: print("[ERROR] Password cannot be empty!")
                    
                    # A 'nonce' is a 'Number used ONCE'. It makes the encryption unique.
                    nonce = secrets.token_bytes(12)
                    combined_data = f"{username}|{password}".encode()
                    ciphertext = aesgcm.encrypt(nonce, combined_data, None)
                    
                    # Save both the encrypted data and the nonce needed to unlock it
                    vault["entries"][service] = {"nonce": nonce.hex(), "data": ciphertext.hex()}
                    save_vault(vault)
                    print(f"[SAVED] {service} encrypted and stored.")

                elif choice2 == "2":
                    # Option to find and decrypt a single password
                    service = get_input("Enter service name (e.g., Google, GitHub...): ").lower()
                    if service in vault["entries"]:
                        entry = vault["entries"][service]
                        nonce = bytes.fromhex(entry["nonce"])
                        ciphertext = bytes.fromhex(entry["data"])
                        
                        try:
                            # Decrypt the binary data back into a readable string
                            decrypted = aesgcm.decrypt(nonce, ciphertext, None).decode()
                            user, pw = decrypted.split("|")
                            print(f"\n[FOUND]\nUsername: {user}\nPassword: {pw}")
                        except:
                            print("[ERROR] Decryption failure.")
                    else:
                        print("[WARN] Service not found.")

                elif choice2 == "3":
                    # Decrypt every single entry in the vault and print it out
                    if not vault["entries"]:
                        print("[WARN] No secrets to display.")
                    else:
                        print("\n" + "="*25)
                        print("FULL VAULT DECRYPTION")
                        print("="*25)
                        for service, data in vault["entries"].items():
                            nonce = bytes.fromhex(data["nonce"])
                            ciphertext = bytes.fromhex(data["data"])
                            try:
                                decrypted = aesgcm.decrypt(nonce, ciphertext, None).decode()
                                user, pw = decrypted.split("|")
                                print(f"SERVICE: {service.upper()}")
                                print(f"  User: {user}")
                                print(f"  Pass: {pw}")
                                print("-" * 20)
                            except:
                                print(f"[ERROR] Could not decrypt {service}")
                        print("="*25)

                elif choice2 == "4":
                    # Permanently remove an entry from the vault dictionary
                    service = get_input("Service to DELETE (e.g., Google, GitHub...): ").lower()
                    if service in vault["entries"]:
                        confirm = get_input(f"[CONFIRM] Permanently delete {service}? (y/n): ")
                        if confirm.lower() == 'y':
                            del vault["entries"][service]
                            save_vault(vault)
                            print(f"[DELETED] {service} removed.")
                        else:
                            print("Deletion cancelled.")
                    else:
                        print("[WARN] Service not found.")

                elif choice2 == "5":
                    # Shows the 'raw' encrypted text (what it looks like in the JSON file)
                    service = get_input("Audit service (e.g., Google, GitHub...): ").lower()
                    if service in vault["entries"]:
                        entry = vault["entries"][service]
                        print(f"\n--- RAW STORAGE AUDIT: {service.upper()} ---")
                        print(f"Ciphertext: {entry['data']}")
                        print(f"Nonce (IV): {entry['nonce']}")
                        print("Algorithm: AES-256-GCM")
                        print("-" * 40)
                    else:
                        print("[WARN] Service not found.")

                elif choice2 == "6":
                    # Exit the inner loop to return to the simple main menu
                    break 
                else:
                    print("[WARN] Invalid selection.")

        elif choice1 == "2":
            # Close the program
            print("Goodbye!")
            break
        else:
            print("[WARN] Invalid selection.")

if __name__ == "__main__":
    # This checks if the script is being run directly rather than imported
    main()

# ---------------------------------------------------------------------------
# Sample Validation Flow (Manual Test Cases)
# ---------------------------------------------------------------------------
"""
1. Initialization: Run script -> Create a Master Password.
   Verify 'vault.json' is created and contains 'salt' and 'test_lock'.

2. Login Logic: Close script -> Run again -> Enter WRONG password.
   Verify 'ACCESS DENIED' message triggers and script terminates.

3. Encryption Logic: Select '1' -> '1' (Add Password) -> Enter 'GitHub', 
   'my_user', and 'p@ssword123'. 
   Verify console shows '[SAVED]'.

4. Search/Decryption: Select '2' (Get Password) -> Enter 'github'.
   Verify 'my_user' and 'p@ssword123' are displayed in plain text.

5. Audit/Persistence: Select '5' (Audit Metadata) -> Enter 'github'.
   Verify that only the Hexadecimal 'Ciphertext' and 'Nonce' are displayed.
   Open 'vault.json' in a text editor to confirm NO plain text exists.

6. Deletion: Select '4' (Delete Entry) -> Enter 'github' -> Confirm 'y'.
   Verify service no longer appears in 'Registered Services' list.
"""
