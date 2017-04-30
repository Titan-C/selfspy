# -*- coding: utf-8 -*-
r"""
Test X sniffer
==============
"""
# Created Sun Apr 30 17:59:32 2017
# Author: Óscar Nájera

from __future__ import division, absolute_import, print_function

from selfspy import sniff_x


def test_keysim():

    assert sniff_x.lookup_keysym(122) == 'z'
    assert sniff_x.lookup_keysym(1225) == '[1225]'
