#!/usr/bin/env python

# Copyright 2012 Bjarte Johansen
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

import os
xdg = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
DATA_DIR = os.path.join(xdg, 'selfspy')
DBNAME = 'selfspy.sqlite'
LOCK_FILE = 'selfspy.pid'
LOCK = None
