# -*- coding: utf-8 -*-
r"""
Total Key press by program
==========================

Show the use of the keyboard in each program
"""
# Author: Óscar Nájera
# License: 3-clause BSD

import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

# Create a SQL connection to our SQLite database and transfer to pandas
#con = sqlite3.connect("/home/oscar/dev/selfspy/.testpy3/selfspy.sqlite")
con = sqlite3.connect("/home/me/dev/selfspy/.test/selfspy.sqlite")

# Select necessary columns
process = pd.read_sql_query("SELECT id, name from process", con,
                            index_col='id')
keys = pd.read_sql_query("SELECT id, process_id, nrkeys from keys", con,
                         index_col='id')
con.close()

total_keypress = keys.groupby('process_id').sum()
total_keypress = pd.merge(total_keypress, process,
                          left_index=True, right_index=True)

total_keypress.sort_values(by='nrkeys', ascending=False)\
    .plot(x='name', kind='bar', logy=True,
          legend=False)
plt.ylabel('Total Key Presses')
plt.xlabel('')
plt.tight_layout()
