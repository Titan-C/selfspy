
# coding: utf-8

# In[37]:


import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

# Create a SQL connection to our SQLite database and transfer to pandas
con = sqlite3.connect("/home/oscar/dev/selfspy/.test/selfspy.sqlite")

# Select necessary columns
process = pd.read_sql_query("SELECT id, name from process", con,
                            index_col='id')
window = pd.read_sql_query("SELECT * from window", con,
                            index_col='id',parse_dates=['created_at'])
keys = pd.read_sql_query("SELECT id, created_at, started, process_id, window_id, timings from keys", con,
                           index_col='id', parse_dates=['created_at', 'started'])
con.close()


# In[5]:


import datetime
d1=datetime.datetime.today()-datetime.timedelta(days=1)


# In[38]:


keys['dwell']=keys['created_at']-keys['started']


# In[39]:


# Total active time
keys['dwell'].sum()


# In[6]:


keys.loc[keys.created_at>d1].tail()


# In[41]:


keys.loc[keys.created_at>d1].groupby('process_id').dwell.sum()


# In[42]:


process


# In[8]:


las=keys.loc[keys.created_at>d1]
las.loc[keys.process_id==1].dwell.sum()


# In[12]:


import json
import zlib
te=json.loads(zlib.decompress(keys.loc[2]['timings']).decode('utf8'))


# In[11]:


keys.loc[2]


# In[13]:


sum(te)


# In[24]:


import time
time.mktime(keys.loc[2].created_at.timetuple())#-0.3


# In[20]:


keys.loc[2]['created_at']


# In[21]:


keys.loc[2]['created_at'].timetuple()


# In[23]:


time.localtime(1502822080.0)


# In[36]:



import selfspy.stats as st
import json
import zlib

def load_timings(timings):
    return json.loads(zlib.decompress(timings))

def create_times(row):
    """Takes a row from the Keys table and returns

    a list with the times of key presses contained in timings

    S----+--+--+--E

"""
    current_time = time.mktime(row.created_at.timetuple())

    abs_times = [current_time]
    for t in load_timings(row.timings):
        current_time -= t
        abs_times.append(current_time)
    abs_times.reverse()
    return abs_times

print(create_times(keys.loc[3]))

print(sum(create_times(keys.loc[3])))

print(load_timings(keys.loc[3].timings))
print(sum(load_timings(keys.loc[3].timings)))
print(keys.loc[3].dwell)

