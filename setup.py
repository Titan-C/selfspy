from __future__ import print_function
import os
import platform
from setuptools import setup

if platform.system() == 'Darwin':
    req_file = 'osx-requirements.txt'
elif platform.system() == "Windows":
    req_file = "win-requirements.txt"
else:
    req_file = 'requirements.txt'

with open(os.path.join(os.path.dirname(__file__), req_file)) as f:
    requires = list(f.readlines())

print('"%s"' % requires)


setup(name="selfspy",
      version='0.3.0',
      packages=['selfspy'],
      author="David Fendrich, Oscar Najera",
      description=''.join("""
          Log everything you do on the computer, for statistics,
          future reference and all-around fun!
      """.strip().split('\n')),
      install_requires=requires,
      entry_points=dict(console_scripts=['selfspy=selfspy:main',
                                         'selfstats=selfspy.stats:main']))
