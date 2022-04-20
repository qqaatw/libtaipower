from Cryptodome.Cipher import DES3
from Cryptodome.Util import Padding
from Cryptodome.Random.random import choice

def get_random_key(bytes: int):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_abcdefghijklmnopqrstuvwxyz"
    return ''.join([choice(chars) for _ in range(bytes)])

def des_encrypt(plain_text: str):
    key = get_random_key(24)
    cipher = DES3.new(key.encode("ascii"), DES3.MODE_ECB)
    encrypted = cipher.encrypt(Padding.pad(plain_text.encode("utf8"), 8))
    return f"{(encrypted).hex()}@{key}"

def des_decrypt(encrypted : str):
    encrypted_text, key = encrypted.split("@")
    cipher = DES3.new(key.encode("ascii"), DES3.MODE_ECB)
    decrypted = cipher.decrypt(bytes.fromhex(encrypted_text))
    return Padding.unpad(decrypted, 8).decode("utf8")