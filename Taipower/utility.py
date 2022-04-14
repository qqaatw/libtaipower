from Cryptodome.Cipher import DES3
from Cryptodome.Util import Padding
from Cryptodome.Random.random import choice

def get_random_key(bytes: int):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_abcdefghijklmnopqrstuvwxyz"
    return ''.join([choice(chars) for _ in range(bytes)])

def des_encrypt(password: str):
    key = get_random_key(24)
    cipher = DES3.new(key.encode(), DES3.MODE_ECB)
    encrypted_pass = cipher.encrypt( Padding.pad(password.encode("ascii"), 8))
    return f"{(encrypted_pass).hex()}@{key}"