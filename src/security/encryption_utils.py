from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
from typing import Dict, Any, Optional

def encrypt_data(data: bytes, master_key: bytes, associated_data: Optional[bytes] = None) -> Dict[str, str]:
    """
    Verschlüsselt Daten mit AES-256-GCM.
    Gibt ein Dictionary mit Chiffretext, IV und Tag zurück (Base64-kodiert).
    """
    nonce = os.urandom(12) # GCM empfiehlt 12 Bytes Nonce

    cipher = Cipher(algorithms.AES(master_key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()

    if associated_data:
        encryptor.authenticate_additional_data(associated_data)

    ciphertext = encryptor.update(data) + encryptor.finalize()
    tag = encryptor.tag

    return {
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "tag": base64.b64encode(tag).decode('utf-8')
    }

def decrypt_data(encrypted_dict: Dict[str, str], master_key: bytes, associated_data: Optional[bytes] = None) -> bytes:
    """
    Entschlüsselt Daten mit AES-256-GCM.
    """
    ciphertext = base64.b64decode(encrypted_dict["ciphertext"])
    nonce = base64.b64decode(encrypted_dict["nonce"])
    tag = base64.b64decode(encrypted_dict["tag"])

    cipher = Cipher(algorithms.AES(master_key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    if associated_data:
        decryptor.authenticate_additional_data(associated_data)

    return decryptor.update(ciphertext) + decryptor.finalize()
