import sys
import glob
from setuptools import setup, find_packages

try:
    if sys.version_info.major != 3:
        sys.stderr.write("Your active Python major version ('%d') is not"
                         " compatible with what KRYPTON expects \n"
                         % sys.version_info.major)
        sys.exit(-1)
except Exception:
    sys.stderr.write("(KRYPTON failed to learn about your Python version.")

setup(
    name='krypton',
    version="0.2.0",
    packages=find_packages(where="krypton"),
    scripts=[script for script in glob.glob('bin/*.py')],
    license="GPLv3+",
)
