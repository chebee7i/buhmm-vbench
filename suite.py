from datetime import datetime
import logging
import os, sys
import glob
import subprocess

from vbench.api import collect_benchmarks

from benchmarks.utils import cd

BASEDIR = os.path.dirname(os.path.realpath(__file__))

log = logging.getLogger('vb')
log.setLevel(logging.INFO)

with cd(os.path.join(BASEDIR, 'benchmarks')):
    filenames = glob.glob("vb*.py")
    names = [filename[:-3] for filename in filenames]
    print(names)
    benchmarks = collect_benchmarks(names)

log.info("Initializing settings")

REPO_PATH = os.path.join(BASEDIR, 'buhmm')
REPO_URL = 'git://github.com/chebee7i/buhmm.git'
REPO_BROWSE = 'https://github.com/chebee7i/buhmm'
DB_PATH = os.path.join(BASEDIR, 'db/benchmarks.db')
TMP_DIR = os.path.join(BASEDIR, 'tmp')

# Assure corresponding directories existence
for s in (REPO_PATH, os.path.dirname(DB_PATH), TMP_DIR):
    if not os.path.exists(s):
        os.makedirs(s)

BRANCHES = ['master']

PREPARE = """
git clean -dfx
"""

BUILD = """
python setup.py build_ext --inplace
"""

START_DATE = datetime(2014, 10, 30)
RST_BASE = 'source'


dependencies = []

DESCRIPTION = ""

HARDWARE = """
Results were collected on the following machine:

  - {uname}
  - CPU: {cpu}
  - Memory: {mem}
  - {dist}
  - Python {python}

``lscpu`` output::

{lscpu}

"""
try:
    subs = {}
    p = subprocess.Popen(['uname', '-srmpio'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    subs['uname'] = out.strip()

    p = subprocess.Popen('cat /proc/cpuinfo | grep --color=no "model name"',
                         shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    out = out.split('\n')[0]
    out = out.split(':')[1].strip()
    subs['cpu'] = out

    p = subprocess.Popen('cat /proc/meminfo | grep --color=no MemTotal',
                         shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    out = out.split('\n')[0]
    out = out.split(':')[1].strip()
    subs['mem'] = out

    try:
        p = subprocess.Popen('cat /etc/lsb-release',
                             shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        # Grab last line
        out = out.strip().split('\n')[-1]
        # Take away quotes in content after equals sign.
        out = out.split('=')[1][1:-1]
        subs['dist'] = out
    except:
        subs['dist'] = ''

    subs['python'] = "{}.{}.{}".format(*sys.version_info[:3])

    p = subprocess.Popen('lscpu', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    subs['lscpu'] = '    '+ '\n    '.join(out.split('\n'))

except:
    pass
else:
    if subs:
        HARDWARE = HARDWARE.format(**subs)
        DESCRIPTION += HARDWARE

    filename = os.path.join(BASEDIR, 'db', 'hardware.txt')
    if os.path.isfile(filename):
        with open(filename) as f:
            data = f.read()
        if data != HARDWARE:
            msg = 'Database exists and was created using different hardware.'
            print(msg)
            print("\nEXISTING:\n{0}".format(data))
            print("\nCURRENT:\n{0}".format(HARDWARE))
    else:
        with open(filename, 'w') as f:
            f.write(HARDWARE)
