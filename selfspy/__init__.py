#!/usr/bin/env python

# Copyright 2012 David Fendrich

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
from selfspy.cipher_dialog import get_keyring_cipher_key, generate_cipherkey, make_encrypter

from selfspy import check_password

from selfspy import config as cfg


def parse_config():
    conf_parser = argparse.ArgumentParser(description=__doc__, add_help=False,
                                          formatter_class=argparse.RawDescriptionHelpFormatter)
    conf_parser.add_argument("-c", "--config",
                             help="Config file with defaults. Command line parameters will override those given in the config file. The config file must start with a \"[Defaults]\" section, followed by [argument]=[value] on each line.", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = {}
    if args.config:
        if not os.path.exists(args.config):
            raise EnvironmentError(
                "Config file %s doesn't exist." % args.config)
        config = configparser.SafeConfigParser()
        config.read([args.config])
        defaults = dict(config.items('Defaults'))
    else:
        if os.path.exists(os.path.expanduser('~/.selfspy/selfspy.conf')):
            config = configparser.SafeConfigParser()
            config.read([os.path.expanduser('~/.selfspy/selfspy.conf')])
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
        cipher_key = generate_cipherkey()

    def check_with_encrypter(cipher_key):
        encrypter = make_encrypter(cipher_key)
        return check_password.check(args['data_dir'], encrypter)

    cipher_key = get_keyring_cipher_key(verify=check_with_encrypter)

    encrypter = make_encrypter(cipher_key)

    if not check_password.check(args['data_dir'], encrypter):
        raise ValueError('Password failed')

    if args["new_cipherkey"]:
        new_cipher_key = generate_cipherkey()
        new_encrypter = make_encrypter(new_cipher_key)
        print('Re-encrypting your keys...')
        astore = ActivityStore(os.path.join(args['data_dir'], cfg.DBNAME),
                               encrypter,
                               store_text=(not args['no_text']),
                               repeat_char=(not args['no_repeat']))
        astore.change_password(new_encrypter)
        # delete the old password.digest
        os.remove(os.path.join(args['data_dir'], check_password.DIGEST_NAME))
        check_password.check(args['data_dir'], new_encrypter)
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
