# -*- coding: utf-8 -*-
r"""
Test for ciphers
================

"""
# Author: Óscar Nájera

from __future__ import division, absolute_import, print_function
import tempfile
import pytest
from selfspy import cipher_dialog


def test_cipher():
    """Test cipher generation"""
    cipher_key = cipher_dialog.generate_cipherkey()
    testdir = tempfile.mkdtemp()

    with pytest.raises(ValueError) as excinfo:
        cipher_dialog.verify_cipher_key(cipher_key, testdir, True)

    cipher_dialog.verify_cipher_key(cipher_key, testdir, False)

    cipher_key = cipher_dialog.generate_cipherkey()
    with pytest.raises(cipher_dialog.InvalidToken) as excinfo:
        cipher_dialog.verify_cipher_key(cipher_key, testdir, False)


def test_make_encrypter():
    """Test bad input"""
    with pytest.raises(IOError) as excinfo:
        cipher_dialog.make_encrypter(None)

    with pytest.raises(ValueError) as excinfo:
        cipher_dialog.make_encrypter('aoei')

    with pytest.raises(ValueError) as excinfo:
        cipher_dialog.make_encrypter(b'aoei')


def test_save_cipher_key():
    """Save a test entry in password-store"""
    # saves the entry
    cipher_dialog.pass_save_cipher_key(b'test', 'testuser')
    # recovers the entry
    assert cipher_dialog.pass_get_cipher_key('testuser') == b'test'
    # fail on missing entry
    with pytest.raises(ValueError) as excinfo:
        cipher_dialog.pass_get_cipher_key('testuser1')
