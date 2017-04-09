# -*- coding: utf-8 -*-
r"""
Cipher functions
================
"""
# Author: Óscar Nájera

import getpass
import keyring
from cryptography.fernet import Fernet


def make_encrypter(cipher_key):
    """Generates a Symmetric encrypt with the cipher_key"""
    if cipher_key is None:
        raise IOError("Cipher Key not found\n"
                      "To setup Selfspy cipher read configuration setup")
    return Fernet(cipher_key)


def get_keyring_cipher_key(verify):
    usr = getpass.getuser()
    cipher_key = keyring.get_password('Selfspy', usr)

    if not verify(cipher_key):
        raise IOError("The cipher key is not valid"
                      "To setup Selfspy cipher read configuration setup")

    return cipher_key


def set_keyring_cipher_key(cipher_key):
    usr = getpass.getuser()
    keyring.set_password('Selfspy', usr, cipher_key)


def generate_cipherkey():
    print("Generating encryption key")
    cipherkey = Fernet.generate_key()
    print("key generated. Saving to Keychain")
    set_keyring_cipher_key(cipherkey)
    return cipherkey
