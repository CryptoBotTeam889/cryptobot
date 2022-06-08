from os.path import isfile
from os.path import dirname
from dotenv import load_dotenv, find_dotenv

# Uncomment next line in case that you create and execute any main function inside this folder.
# load_dotenv(find_dotenv())

version_file = '{}/version.txt'.format(dirname(__file__))

if isfile(version_file):
    with open(version_file) as version_file:
        __version__ = version_file.read().strip()
