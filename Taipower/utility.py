from Cryptodome.Cipher import DES3
from Cryptodome.Util import Padding
from Cryptodome.Random.random import choice


def get_random_key(bytes: int) -> str:
    """Generate a random key from a list of characters.

    Parameters
    ----------
    bytes : int
        The number of bytes of the key.

    Returns
    -------
    str
        Random key.
    """

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_abcdefghijklmnopqrstuvwxyz"
    return ''.join([choice(chars) for _ in range(bytes)])

def des_encrypt(plain_text: str):
    """Encrypt text with a random key using Triple DES.

    Parameters
    ----------
    plain_text : str
        Text to be encrypted.

    Returns
    -------
    str
        Encrypted text.
    """

    key = get_random_key(24)
    cipher = DES3.new(key.encode("ascii"), DES3.MODE_ECB)
    encrypted = cipher.encrypt(Padding.pad(plain_text.encode("utf8"), 8))
    return f"{(encrypted).hex()}@{key}"

def des_decrypt(encrypted : str):
    """Decrypt text using Triple DES.

    Parameters
    ----------
    encrypted : str
        Encrypted text.

    Returns
    -------
    str
        Decrypted plain text.
    """

    encrypted_text, key = encrypted.split("@")
    cipher = DES3.new(key.encode("ascii"), DES3.MODE_ECB)
    decrypted = cipher.decrypt(bytes.fromhex(encrypted_text))
    return Padding.unpad(decrypted, 8).decode("utf8")

def roc_year_to_wastern(date_text : str) -> str:
    """Convert ROC year to wastern year.

    Parameters
    ----------
    date_text : str
        `yyy...`.

    Returns
    -------
    str
        `yyyy...`
    """

    assert len(date_text) >= 7, "The `date_text` should be in `yyy...` format."

    return f"{ str( 1911 + int(date_text[0:3])) }{date_text[3:]}"