import crypto

# 🔥 Optimized: Using 4 characters to store 2 bits per char (Base4 Stego)
ZWC = {
    "00": '\u200B', # Zero Width Space
    "01": '\u200C', # Zero Width Non-Joiner
    "10": '\u200D', # Zero Width Joiner
    "11": '\u2063'  # Invisible Separator (Safe for wrapping)
}
# Reverse lookup for revealing
REV_ZWC = {v: k for k, v in ZWC.items()}

def hide_text(cover_text: str, secret_text: str, password: str) -> str:
    """Encrypts a secret and hides it invisibly at the very end of the cover text."""
    
    enc_data, salt, nonce = crypto.encrypt_data(secret_text.encode('utf-8'), password)
    payload = salt + nonce + enc_data
    
    # Convert bytes to a bit string
    bin_str = ''.join(format(byte, '08b') for byte in payload)
    
    # Map bits in pairs of 2 to ZWC
    hidden_payload = ""
    for i in range(0, len(bin_str), 2):
        pair = bin_str[i:i+2]
        hidden_payload += ZWC[pair]
    
    # 🔥 THE FIX: Append to the end. No interleaving, no letter spacing!
    return cover_text + hidden_payload

def reveal_text(stego_text: str, password: str) -> str:
    """Extracts invisible characters, decrypts, and reveals the secret."""
    
    # Siphon out ONLY the invisible characters from the text
    hidden_chars = [c for c in stego_text if c in REV_ZWC]
    if not hidden_chars: 
        raise ValueError("No hidden data detected in this text.")
    
    # Convert invisible characters back to a binary string
    bin_str = ''.join(REV_ZWC[c] for c in hidden_chars)
    
    # Convert the binary string back to raw bytes
    payload = bytearray(int(bin_str[i:i+8], 2) for i in range(0, len(bin_str), 8))
    payload_bytes = bytes(payload)
    
    # Unpack metadata and decrypt
    try:
        salt = payload_bytes[:16]
        nonce = payload_bytes[16:28]
        enc_data = payload_bytes[28:]
        
        dec = crypto.decrypt_data(enc_data, password, salt, nonce)
        return dec.decode('utf-8')
    except Exception: 
        raise ValueError("Decryption failed. Incorrect password or tampered text.")