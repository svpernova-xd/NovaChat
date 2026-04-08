import struct

MAGIC_HEADER = b"NV01"

def pack_nv_file(filename: str, salt: bytes, nonce: bytes, encrypted_data: bytes) -> bytes:
    """Packs the components into the custom .nv binary format."""
    filename_bytes = filename.encode('utf-8')
    filename_length = len(filename_bytes)
    
    format_string = f">4sI{filename_length}s16s12s"
    
    header = struct.pack(
        format_string,
        MAGIC_HEADER,
        filename_length,
        filename_bytes,
        salt,
        nonce
    )
    
    return header + encrypted_data

def unpack_nv_file(file_data: bytes) -> tuple[str, bytes, bytes, bytes]:
    """
    Unpacks the custom .nv binary format.
    Returns: (original_filename, salt, nonce, encrypted_data)
    """
    # Check the magic identifier
    magic = file_data[:4]
    if magic != MAGIC_HEADER:
        raise ValueError("Invalid file format. [NV01] magic header missing.")
        
    # Extract the filename length (4-byte unsigned integer)
    filename_length = struct.unpack(">I", file_data[4:8])[0]
    
    # Calculate byte offsets for slicing
    filename_end = 8 + filename_length
    salt_end = filename_end + 16
    nonce_end = salt_end + 12
    
    # Slice the byte array into our components
    filename = file_data[8:filename_end].decode('utf-8')
    salt = file_data[filename_end:salt_end]
    nonce = file_data[salt_end:nonce_end]
    encrypted_data = file_data[nonce_end:]
    
    return filename, salt, nonce, encrypted_data