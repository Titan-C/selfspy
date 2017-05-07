# -*- coding: utf-8 -*-
r"""
Cipher functions
================
"""
# Author: Óscar Nájera

import os
import getpass
import keyring
from cryptography.fernet import Fernet, InvalidToken


def generate_cipherkey():
    """Generates  a Fernet cipherkey

    If save is True saves the key in keyring

    .. seealso::
        https://github.com/pyca/cryptography
"""
    print("Generating encryption key")
    cipherkey = Fernet.generate_key()
    print("Key generated.")

    return cipherkey


def make_encrypter(cipher_key):
    """Returns a Fernet Symmetric encryptor with the cipher_key"""
    if cipher_key is None:
        raise IOError("Cipher Key not found\n"
                      "To setup Selfspy cipher read configuration setup")
    return Fernet(cipher_key)


def verify_cipher_key(cipher_key, data_dir, read_only):
    """Verify cipher key to unlock database

    Parameters
    ----------
    cipher_key : bytes

    data_dir : string
        directory where database is stored
    read_only : bool
        Read directory only. If false save cipher key verification

    Raises
    ------
    InvalidToken
        cipher_key can't be used for decryption
    ValueError
        Invalid key
    """

    encrypter = make_encrypter(cipher_key)
    try:
        sucess = check(data_dir, encrypter, read_only)
    except InvalidToken:
        raise InvalidToken("The cipher key is not valid for decryption"
                           "To setup Selfspy cipher read configuration setup")

    if not sucess:
        raise ValueError("The cipher setup is not valid\n"
                         "To setup Selfspy cipher read configuration setup")


def get_keyring_cipher_key():
    """Recover cipher_key from keyring"""
    user = getpass.getuser()
    return keyring.get_password('Selfspy', user)


def save_keyring_cipher_key(cipher_key):
    """Save cipher_key in keyring"""
    print("Saving cipher key to Keychain")
    usr = getpass.getuser()
    keyring.set_password('Selfspy', usr, cipher_key)


###############################################################################
DIGEST_NAME = 'password.digest'
MAGIC_STRING = b'\xc5\x7fdh\x05\xf6\xc5=\xcfh\xafv\xc0\xf4\x13i*.O\xf6\xc2\x8d\x0f\x87\xdb\x9f\xc2\x88\xac\x95\xf8\xf0\xf4\x96\xe9\x82\xd1\xca[\xe5\xa32\xa0\x03\nD\x12\n\x1dr\xbc\x03\x9bE\xd3q6\x89Cwi\x10\x92\xdf(#\x8c\x87\x1b3\xd6\xd4\x8f\xde)\xbe\x17\xbf\xe4\xae\xb73\\\xcb\x7f\xd3\xc4\x89\xd0\x88\x07\x90\xd8N,\xbd\xbd\x93j\xc7\xa3\xec\xf3P\xff\x11\xde\xc9\xd6 \x98\xe8\xbc\xa0|\x83\xe90Nw\xe4=\xb53\x08\xf0\x14\xaa\xf9\x819,X~\x8e\xf7mB\x13\xe9;\xde\x9e\x10\xba\x19\x95\xd4p\xa7\xd2\xa9o\xbdF\xcd\x83\xec\xc5R\x17":K\xceAiX\xc1\xe8\xbe\xb8\x04m\xbefA8\x99\xee\x00\x93\xb4\x00\xb3\xd4\x8f\x00@Q\xe9\xd5\xdd\xff\x8d\x93\xe3w6\x8ctRQK\xa9\x97a\xc1UE\xdfv\xda\x15\xf5\xccA)\xec^]AW\x17/h)\x12\x89\x15\x0e#8"\x7f\x16\xd6e\x91\xa6\xd8\xea \xb9\xdb\x93W\xce9\xf2a\xe7\xa7T=q'


def check(data_dir, decrypter, read_only=False):
    """Check decrypter is able to read current ciphered data"""
    fname = os.path.join(data_dir, DIGEST_NAME)
    if os.path.exists(fname):
        with open(fname, 'rb') as f:
            s = f.read()
        return decrypter.decrypt(s) == MAGIC_STRING
    else:
        if decrypter is not None and not read_only:
            with open(fname, 'wb') as f:
                f.write(decrypter.encrypt(MAGIC_STRING))
            return True
    return False
