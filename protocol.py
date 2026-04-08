import crypto

DELIM = b"::NOVA::"

def encode_message(msg: str, password: str):
    payload = crypto.create_payload(msg, password)
    return payload.encode() + DELIM

def decode_message(data: bytes, password: str):
    payload = data.replace(DELIM, b"").decode()
    return crypto.extract_payload(payload, password)

def encode_file_alert(sender, filename, size):
    return f"FILE_ALERT::{sender}::{filename}::{size}".encode()

def encode_file_payload(sender, target_user, filename, file_bytes, password):
    # 🔐 Encrypts the file before it leaves the sender's machine
    encrypted_data, salt, nonce = crypto.encrypt_data(file_bytes, password)
    
    # Pack the sender, target, and filename into the header
    header = f"{sender}::{target_user}::{filename}|".encode()
    
    # 🚀 Add the stream-ending delimiter to beat TCP Fragmentation
    return b"FILE_DATA::" + header + salt + nonce + encrypted_data + b"::NOVA_FILE_END::"

def decode_file_payload(blob, password):
    # 🔓 Decrypts the file securely on the receiver's machine
    salt = blob[:16]
    nonce = blob[16:28]
    encrypted_data = blob[28:]
    return crypto.decrypt_data(encrypted_data, password, salt, nonce)