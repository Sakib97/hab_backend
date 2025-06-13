from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os
from dotenv import load_dotenv
from core.jwtHandler import JWT_SECRET, JWT_ALGORITHM

# def encrypt_email(email: str) -> str:
#     cipher = AES.new(JWT_SECRET, AES.MODE_CBC)
#     ct_bytes = cipher.encrypt(pad(email.encode(), AES.block_size))
#     iv = cipher.iv
#     return base64.urlsafe_b64encode(iv + ct_bytes).decode('utf-8').rstrip('=')

# def decrypt_email(encrypted: str) -> str:
#     data = base64.urlsafe_b64decode(encrypted + '=' * (-len(encrypted) % 4))
#     iv, ct = data[:16], data[16:]
#     cipher = AES.new(JWT_SECRET, AES.MODE_CBC, iv)
#     return unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')

def xor_encode(input_str: str, key: int = 42) -> str:
    # Convert string to bytes
    input_bytes = input_str.encode('utf-8')
    # XOR each byte with the key
    xored_bytes = bytes([b ^ key for b in input_bytes])
    # Base64 encode the XORed bytes for safe transmission as string
    encoded_str = base64.b64encode(xored_bytes).decode('utf-8')
    return encoded_str

def xor_decode(encoded_str: str, key: int = 42) -> str:
    # Base64 decode to get xored bytes
    xored_bytes = base64.b64decode(encoded_str)
    # XOR again with the key to get original bytes
    original_bytes = bytes([b ^ key for b in xored_bytes])
    # Convert bytes back to string
    return original_bytes.decode('utf-8')