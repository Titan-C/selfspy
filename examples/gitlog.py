# -*- coding: utf-8 -*-
r"""
Analyzing git history
=====================

Scan a git repo commit history
"""
# Created: Sun Nov 19 17:57:18 2017
# Author: Óscar Nájera
# License: 3-clause BSD
import matplotlib.pyplot as plt
import pandas as pd

series = pd.read_csv('log', names=['Author', 'date'],
                     parse_dates=['date'], index_col='date')

###########################################################################
# Total Commits
# -------------

commits = series.groupby('Author').resample('2W').count()
commits.columns = ['commits']
commits.plot(kind='area')

###########################################################################
# Commits by author
# -----------------

authors_commits = series.groupby('Author').resample('2W').count()
authors_commits.columns = ['commits']
authors_commits.unstack(level=0).fillna(0).plot(
    kind='area', subplots=True, figsize=(8, 30), layout=(15, 2))
