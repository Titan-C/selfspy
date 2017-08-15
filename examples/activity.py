
# coding: utf-8

# In[37]:

import time
import json
import zlib
import datetime
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

import selfspy.stats as st

# Create a SQL connection to our SQLite database and transfer to pandas
con = sqlite3.connect(os.path.expanduser("~/dev/selfspy/.test/selfspy.sqlite"))

# Select necessary columns
process = pd.read_sql_query("SELECT id, name from process", con,
                            index_col='id')
window = pd.read_sql_query("SELECT * from window", con,
                           index_col='id', parse_dates=['created_at'])
keys = pd.read_sql_query("SELECT id, created_at, started, process_id, window_id, timings from keys", con,
                         index_col='id', parse_dates=['created_at', 'started'])
con.close()


keys['dwell'] = keys['created_at'] - keys['started']
# Total active time of recording
keys['dwell'].max()

# The activity intervals
starts = keys.started.value_counts()
ends = keys.created_at.value_counts()
df2 = pd.concat([starts, ends], axis=1, keys=['enter', 'exit'])
df2.fillna(0, inplace=True)
df2['diff'] = df2['enter'] - df2['exit']
counts = df2["diff"].resample("5min").sum().fillna(0).cumsum()
counts.plot()
plt.show()

# The activity intervals by process not working
starts = keys.groupby('process_id').started.value_counts()
ends = keys.groupby('process_id').created_at.value_counts()
df2 = pd.concat([starts, ends], axis=1, keys=['enter', 'exit'])
df2.fillna(0, inplace=True)
df2['diff'] = df2['enter'] - df2['exit']
counts = df2["diff"].resample("5min").sum().fillna(0).cumsum()
counts.plot()
plt.show()

# filter by last 2 weeks
d1 = datetime.datetime.today() - datetime.timedelta(weeks=2)
keys.loc[keys.created_at > d1]

# filter by process
las = keys.loc[keys.created_at > d1]
las.loc[keys.process_id == 1].dwell.sum()


# # testing the functions
# In[20]:


keys.loc[2]['created_at']


# In[21]:


keys.loc[2]['created_at'].timetuple()


# In[23]:


time.localtime(1502822080.0)


# In[36]:


print(create_times(keys.loc[3]))

print(sum(create_times(keys.loc[3])))

print(load_timings(keys.loc[3].timings))
print(sum(load_timings(keys.loc[3].timings)))
print(keys.loc[3].dwell)
