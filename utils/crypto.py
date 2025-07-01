from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

backend = default_backend()

def gerar_chave_mestra(senha_login: str, salt: bytes) -> bytes:
    """Gera chave mestra com PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend
    )
    return kdf.derive(senha_login.encode())

def criptografar(dado: str, chave: bytes, iv: bytes) -> bytes:
    """Criptografa com AES CBC"""
    cipher = Cipher(algorithms.AES(chave), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    # PKCS7 Padding manual
    pad = 16 - len(dado.encode()) % 16
    dado_padded = dado.encode() + bytes([pad] * pad)
    return encryptor.update(dado_padded) + encryptor.finalize()

def descriptografar(dado_cript: bytes, chave: bytes, iv: bytes) -> str:
    cipher = Cipher(algorithms.AES(chave), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    dados = decryptor.update(dado_cript) + decryptor.finalize()
    pad = dados[-1]
    return dados[:-pad].decode()

def gerar_recovery_key():
    return base64.urlsafe_b64encode(os.urandom(24)).decode()  # ex: 32 chars

def derivar_chave_da_recovery(recovery_key: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend
    )
    return kdf.derive(recovery_key.encode())

def criptografar_chave_mestra(chave_mestra: bytes, chave_recovery: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(chave_recovery), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    pad = 16 - len(chave_mestra) % 16
    chave_padded = chave_mestra + bytes([pad] * pad)
    return encryptor.update(chave_padded) + encryptor.finalize()

