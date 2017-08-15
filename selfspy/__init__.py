#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Selfspy
=======

Goal of the script
"""
# Copyright 2012 David Fendrich
# Copyright 2017 Oscar Najera

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

from __future__ import division, absolute_import, print_function

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
                             help="Config file with defaults. Command line "
                             "parameters will override those given in the "
                             "config file. The config file must start with "
                             "a \"[Defaults]\" section, followed by"
                             "[argument]=[value] on each line.", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = {}
    config = configparser.ConfigParser()
    if args.config:
        if not os.path.exists(args.config):
            raise FileNotFoundError(
                "Config file %s doesn't exist." % args.config)
        config.read([args.config])
        defaults = dict(config.items('Defaults'))
    else:
        default_conf_file = os.path.expanduser('~/.selfspy/selfspy.conf')
        if os.path.exists(default_conf_file):
            config.read(default_conf_file)
            defaults = dict(config.items('Defaults'))

    parser = argparse.ArgumentParser(
        description="""Monitor your computer activities and store them in
        an encrypted database for later analysis or disaster recovery.""",
        parents=[conf_parser])

    parser.set_defaults(**defaults)
    parser.add_argument('--setup', action="store_true",
                        help="First time setting up Selfspy")
    parser.add_argument('-d', '--data-dir', help='Data directory for selfspy, where the database is stored. Remember that Selfspy must have read/write access. Default is %s' %
                        cfg.DATA_DIR, default=cfg.DATA_DIR)

    parser.add_argument('-n', '--no-text', action='store_true', help='Do not store what you type. This will make your database smaller and less sensitive to security breaches. Process name, window titles, window geometry, mouse clicks, number of keys pressed and key timings will still be stored, but not the actual letters. Key timings are stored to enable activity calculation in selfstats. If this switch is used, you will never be asked for password.')
    parser.add_argument('-r', '--no-repeat', action='store_true',
                        help='Do not store special characters as repeated characters.')


    return parser.parse_args()




def main():
    args = vars(parse_config())

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
