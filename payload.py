import base64
import textwrap

def create_payload(nv_binary: bytes) -> str:
    """Converts an encrypted .nv binary into a copy-pasteable Base64 block."""
    # Convert binary to base64 string
    b64_string = base64.b64encode(nv_binary).decode('utf-8')
    
    # Wrap text to 76 characters per line (Standard MIME/PEM format)
    wrapped_b64 = textwrap.fill(b64_string, width=76)
    
    return f"-----BEGIN NOVA PAYLOAD-----\n{wrapped_b64}\n-----END NOVA PAYLOAD-----"

def extract_payload(payload_string: str) -> bytes:
    """Extracts and decodes the Base64 block back into .nv binary."""
    if "-----BEGIN NOVA PAYLOAD-----" not in payload_string or "-----END NOVA PAYLOAD-----" not in payload_string:
        raise ValueError("Invalid Nova Payload format. Missing header/footer.")
        
    # Extract just the Base64 part between the headers
    start = payload_string.find("-----BEGIN NOVA PAYLOAD-----") + len("-----BEGIN NOVA PAYLOAD-----")
    end = payload_string.find("-----END NOVA PAYLOAD-----")
    
    b64_data = payload_string[start:end].strip()
    
    # Remove any internal newlines or spaces
    clean_b64 = "".join(b64_data.split())
    
    try:
        return base64.b64decode(clean_b64)
    except Exception as e:
        raise ValueError(f"Base64 decoding failed: {e}")