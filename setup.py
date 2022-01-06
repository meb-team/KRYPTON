import sys
from setuptools import setup

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
    version="0.1.0",
    packages=['krypton'],
    scripts=['bin/KRYPTON.py'],
    license="GPLv3+",
)
