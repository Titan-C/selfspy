#!/usr/bin/env python

# Copyright 2012 David Fendrich
# Copyright 2017 Oscar Najera

# This file is part of Selfspy

# Selfspy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Selfspy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Selfspy.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import os
import sys
import fcntl

import argparse
import configparser

from selfspy.activity_store import ActivityStore
from selfspy import cipher_dialog
from selfspy import config as cfg


def parse_config():
    conf_parser = argparse.ArgumentParser(description=__doc__, add_help=False,
                                          formatter_class=argparse.RawDescriptionHelpFormatter)
    conf_parser.add_argument("-c", "--config",
                             help="Config file with defaults. Command line parameters will override those given in the config file. The config file must start with a \"[Defaults]\" section, followed by [argument]=[value] on each line.", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = {}
    config = configparser.ConfigParser()
    if args.config:
        if not os.path.exists(args.config):
            raise EnvironmentError(
                "Config file %s doesn't exist." % args.config)
        config.read([args.config])
        defaults = dict(config.items('Defaults'))
    else:
        default_conf_file = os.path.expanduser('~/.selfspy/selfspy.conf')
        if os.path.exists(default_conf_file):
            config.read(default_conf_file)
            defaults = dict(config.items('Defaults'))

    parser = argparse.ArgumentParser(
        description='Monitor your computer activities and store them in an encrypted database for later analysis or disaster recovery.', parents=[conf_parser])

    parser.set_defaults(**defaults)
    parser.add_argument('--setup', action="store_true",
                        help="First time setting up Selfspy")
    parser.add_argument('-d', '--data-dir', help='Data directory for selfspy, where the database is stored. Remember that Selfspy must have read/write access. Default is %s' %
                        cfg.DATA_DIR, default=cfg.DATA_DIR)

    parser.add_argument('-n', '--no-text', action='store_true', help='Do not store what you type. This will make your database smaller and less sensitive to security breaches. Process name, window titles, window geometry, mouse clicks, number of keys pressed and key timings will still be stored, but not the actual letters. Key timings are stored to enable activity calculation in selfstats. If this switch is used, you will never be asked for password.')
    parser.add_argument('-r', '--no-repeat', action='store_true',
                        help='Do not store special characters as repeated characters.')

    parser.add_argument('--new_cipherkey', action="store_true",
                        help='Change the cipher key used to encrypt the keys columns and exit.')

    return parser.parse_args()


def new_cipher(decrypter, args):
    """Encrypt database with new decrypter

    Parameters
    ----------
    decrypter : function to decrypt database

    args : dictionary
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


def main():
    try:
        args = vars(parse_config())
    except EnvironmentError as e:
        print(str(e))
        sys.exit(1)

    args['data_dir'] = os.path.expanduser(args['data_dir'])
    os.makedirs(args['data_dir'], exist_ok=True)

    lockname = os.path.join(args['data_dir'], cfg.LOCK_FILE)
    cfg.LOCK = open(lockname, 'w')
    try:
        fcntl.lockf(cfg.LOCK, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print('%s is locked! I am probably already running.' % lockname)
        print('If you can find no selfspy process running, it is a stale lock and you can safely remove it.')
        print('Shutting down.')
        sys.exit(1)

    if args["setup"]:
        cipher_key = cipher_dialog.generate_cipherkey()
        cipher_dialog.save_keyring_cipher_key(cipher_key)

    cipher_key = cipher_dialog.get_keyring_cipher_key()
    cipher_dialog.verify_cipher_key(cipher_key, args["data_dir"], True)

    encrypter = cipher_dialog.make_encrypter(cipher_key)

    if not cipher_dialog.check(args['data_dir'], encrypter):
        raise ValueError('Password failed')

    if args["new_cipherkey"]:
        new_cipher(encrypter, args)
        # don't assume we want the logger to run afterwards
        print('Exiting...')
        sys.exit(0)

    astore = ActivityStore(os.path.join(args['data_dir'], cfg.DBNAME),
                           encrypter,
                           store_text=(not args['no_text']),
                           repeat_char=(not args['no_repeat']))

    try:
        astore.run()
    except SystemExit:
        astore.close()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
