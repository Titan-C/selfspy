# -*- coding: utf-8 -*-
r"""
Analyzing git history lines changed
===================================

Scan a git repo commit history
"""
# Created: Sun Nov 19 17:57:18 2017
# Author: Óscar Nájera
# License: 3-clause BSD
from datetime import datetime
import re
import shlex
import subprocess
import matplotlib.pyplot as plt
import pandas as pd

###########################################################################
# Obtain git commit data
# ----------------------

log = subprocess.run(shlex.split("git log --shortstat --no-merges --format='%aN, %at'"),
                     stdout=subprocess.PIPE, encoding='utf-8').stdout


commit_pattern = re.compile(
    "^(?P<author>.*), (?P<stamp>\d*)\s+(?P<files_changed>\d+) files? changed.*?(?:(?P<insertions>\d+) insertions?.*?)?(?:(?P<deletions>\d+) deletions?.*?)?$", flags=re.M)


with open('log', 'w') as filelog:
    for match in re.finditer(commit_pattern, log):
        parsed = re.sub("None", "0", ";".join(map(str, match.groups())) + '\n')
        filelog.write(parsed)


commits = pd.read_csv('log', names=['author', 'date', 'files_changed',
                                    'insertions', 'deletions'],
                      date_parser=lambda x: datetime.fromtimestamp(int(x)),
                      parse_dates=['date'], index_col='date',
                      delimiter=';',
                      dtype={'author': 'category', 'files_changed': 'int32',
                             'insertions': 'int32', 'deletions': 'int32'})

plt.subplot(211)
lines_edited = commits.resample('W').sum().fillna(0)
lines_edited.insertions.plot(kind='area')

deleted = - lines_edited.deletions
deleted.plot(kind='area')
plt.ylim(-600, 1000)
plt.ylabel('lines edited')

plt.subplot(212)
total_lines = lines_edited.insertions - lines_edited.deletions
total_lines.cumsum().plot(style=['C2'])
plt.ylabel('total lines')

plt.show()
