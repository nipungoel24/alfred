import sys
import base64

def _win_encrypt(data: bytes) -> bytes:
    import ctypes
    from ctypes import wintypes
    crypt32 = ctypes.windll.crypt32
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.BYTE))]
    in_blob = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.BYTE)))
    out_blob = DATA_BLOB()
    res = crypt32.CryptProtectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob))
    if not res:
        raise OSError("CryptProtectData failed")
    enc_data = ctypes.string_at(out_blob.pbData, out_blob.cbData)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return enc_data

def _win_decrypt(enc_data: bytes) -> bytes:
    import ctypes
    from ctypes import wintypes
    crypt32 = ctypes.windll.crypt32
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.BYTE))]
    in_blob = DATA_BLOB(len(enc_data), ctypes.cast(ctypes.create_string_buffer(enc_data), ctypes.POINTER(ctypes.BYTE)))
    out_blob = DATA_BLOB()
    res = crypt32.CryptUnprotectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob))
    if not res:
        raise OSError("CryptUnprotectData failed")
    dec_data = ctypes.string_at(out_blob.pbData, out_blob.cbData)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return dec_data

def encrypt_token(token: str) -> bytes:
    if not token:
        return b""
    data_bytes = token.encode('utf-8')
    if sys.platform == 'win32':
        try:
            return _win_encrypt(data_bytes)
        except Exception:
            pass
    # Fallback/plaintext encoding
    return base64.b64encode(data_bytes)

def decrypt_token(enc_data: bytes) -> str:
    if not enc_data:
        return ""
    if sys.platform == 'win32':
        try:
            return _win_decrypt(enc_data).decode('utf-8')
        except Exception:
            pass
    # Fallback/plaintext decoding
    try:
        return base64.b64decode(enc_data).decode('utf-8')
    except Exception:
        try:
            return enc_data.decode('utf-8', errors='replace')
        except Exception:
            return ""
