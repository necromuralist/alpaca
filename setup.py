import sys

if sys.version_info < (3, 0):
    sys.exit(
        ("This doesn't support python 2,"
         " it doesn't support {0}").format(sys.version))

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

setup(name='packets',
      version='2018.6.4',
      description=("Code to pull some packet-files."),
      author="russell",
      platforms=['linux'],
      url='https://github.azc.ext.hp.com/russell-nakamura1/packets',
      author_email="russell.nakamura1@hp.com",
      packages=find_packages(),
      entry_points="""
      [console_scripts]
      packets=packets.main:main
      """
      )
