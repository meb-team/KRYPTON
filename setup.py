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
    scripts=[script for script in glob.glob('bin/*.py')],
    packages=find_packages(),
    package_data={"":
                  [
                   "ressources/AntiFam.hmm*",
                   "ressources/KEGG_data/*.tsv"
                   ]
                  },
    license="GPLv3+",
    url="https://github.com/meb-team/KRYPTON",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: " +
        "GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
