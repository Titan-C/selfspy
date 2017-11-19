# -*- coding: utf-8 -*-
r"""
Analyzing git history
=====================

Scan a git repo commit history
"""
# Created: Sun Nov 19 17:57:18 2017
# Author: Óscar Nájera
# License: 3-clause BSD
import shlex
import subprocess
import matplotlib.pyplot as plt
import pandas as pd

###########################################################################
# Obtain git commit data
# ----------------------

log = subprocess.run(shlex.split("git log --format=' % aN, % ad'"),
                     stdout=subprocess.PIPE, encoding='utf-8')

with open('log', 'w') as filelog:
    filelog.write(log.stdout)

series = pd.read_csv('log', names=['author', 'date'],
                     parse_dates=['date'], index_col='date',
                     dtype={'author': 'category'})

###########################################################################
# Total Commits
# -------------

commits = series.resample('2W').count()
commits.columns = ['commits']
commits.plot(kind='area')

###########################################################################
# Commits by author
# -----------------

authors_commits = series.groupby('author').resample('2W').count()
authors_commits.columns = ['commits']
authors_commits.unstack(level=0).fillna(0).plot(
    kind='area', subplots=True, figsize=(11, 30), layout=(15, 2))
