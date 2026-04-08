import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return kdf.derive(password.encode())


def encrypt_data(data: bytes, password: str):
    salt = os.urandom(16)
    nonce = os.urandom(12)

    key = derive_key(password, salt)
    aes = AESGCM(key)

    encrypted = aes.encrypt(nonce, data, None)
    return encrypted, salt, nonce


def decrypt_data(enc, password, salt, nonce):
    key = derive_key(password, salt)
    aes = AESGCM(key)
    return aes.decrypt(nonce, enc, None)


# 🔐 payload system
def create_payload(text: str, password: str) -> str:
    data = text.encode()
    enc, salt, nonce = encrypt_data(data, password)
    blob = salt + nonce + enc
    return "NOVA::" + base64.urlsafe_b64encode(blob).decode()


def extract_payload(payload: str, password: str) -> str:
    encoded = payload.split("NOVA::", 1)[1]
    blob = base64.urlsafe_b64decode(encoded)

    salt = blob[:16]
    nonce = blob[16:28]
    enc = blob[28:]

    return decrypt_data(enc, password, salt, nonce).decode()


# 🔥 file encryption (separate key)
def encrypt_with_key(data: bytes, key: bytes):
    nonce = os.urandom(12)
    aes = AESGCM(key)
    return aes.encrypt(nonce, data, None), nonce


def decrypt_with_key(data: bytes, key: bytes, nonce: bytes):
    aes = AESGCM(key)
    return aes.decrypt(nonce, data, None)