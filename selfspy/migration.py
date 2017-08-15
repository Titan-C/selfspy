# -*- coding: utf-8 -*-
r"""
Database change tools
=====================

Change encryption keys
"""
# Created: Tue Aug 15 13:56:20 2017
# Author: Óscar Nájera
# License: GPL-3

from __future__ import division, absolute_import, print_function

def new_cipher(decrypter, args):
    """Encrypt database with new decrypter

    Parameters
    - ---------
    decrypter: function to decrypt database

    args: dictionary
        Setup arguments

    """
    new_cipher_key = cipher_dialog.generate_cipherkey()
    cipher_dialog.save_keyring_cipher_key(new_cipher_key)

    new_encrypter = cipher_dialog.make_encrypter(new_cipher_key)
    print('Re-encrypting your keys...')
    astore = ActivityStore(os.path.join(args['data_dir'], cfg.DBNAME),
                           decrypter,
                           store_text=(not args['no_text']),
                           repeat_char=(not args['no_repeat']))
    astore.change_password(new_encrypter)
    # delete the old password.digest
    os.remove(os.path.join(args['data_dir'], cipher_dialog.DIGEST_NAME))
    cipher_dialog.check(args['data_dir'], new_encrypter)

    ######################
    parser.add_argument('--new_cipherkey', action="store_true",
                        help='Change the cipher key used to encrypt the keys columns and exit.')

    if args["new_cipherkey"]:
        new_cipher(encrypter, args)
        # don't assume we want the logger to run afterwards
        print('Exiting...')
        sys.exit(0)
