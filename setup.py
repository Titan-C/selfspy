from __future__ import print_function
import os
from setuptools import setup

req_file = 'requirements.txt'

with open(os.path.join(os.path.dirname(__file__), req_file)) as f:
    requires = f.read().split()


setup(name="selfspy",
      version='0.3.0',
      packages=['selfspy'],
      author="David Fendrich, Oscar Najera",
      description=''.join("""
          Log everything you do on the computer, for statistics,
          future reference and all-around fun!
      """.strip().split('\n')),
      install_requires=requires,
      setup_requires=['sphinx', 'pytest-runner'],
      tests_require=['pytest-cov', 'pytest'],  # Somehow this order is relevant
      entry_points=dict(console_scripts=['selfspy=selfspy:main',
                                         'selfstats=selfspy.stats:main']))
