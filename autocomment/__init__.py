from os.path import dirname
from pkg_resources import resource_filename

version_file = resource_filename('autocomment', 'VERSION')

with open(version_file, 'r') as f:
    VERSION = f.read().strip()
BASE_DIR = dirname(dirname(__file__))
