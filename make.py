#!/usr/bin/env python
# coding: utf8
"""
Python script for building documentation.

Note: currently latex builds do not work because of table formats that are not
supported in the latex generation.

Usage
-----
python make.py clean
python make.py html

"""
from __future__ import print_function

import glob
import os
import shutil
import sys
import sphinx

import matplotlib
matplotlib.use('Agg')
import seaborn

from benchmarks.utils import cd

BASEDIR = os.path.dirname(os.path.realpath(__file__))
# This allows us to import from the "benchmarks" folder.
sys.path.insert(0, BASEDIR)
sys.path.insert(0, os.path.join(BASEDIR, 'benchmarks'))

# Use vbench from this folder.
sys.path.insert(0, os.path.join(BASEDIR, 'vbench'))

SPHINX_BUILD = 'sphinxbuild'

def update():
    """
    Update and rebuild. A commit will be required if a merge is successful.

    Note, we do not update vbench.
    If/when we want to do this, then we will do it manually.

    """
    # Verifying the benchmarks may require building, so we always build.
    from suite import REPO_PATH
    cmds = [
        'cd {0}'.format(REPO_PATH),
        'git pull --ff-only',
        'python setup.py build_ext --in-place'
    ]
    os.system(';'.join(cmds))

def upload():
    """
    Upload a copy of the benchmark reports to the gh-pages branch.

    """
    print("Removing previous gh-pages branches locally and also from origin.")
    cmds = [
        'git branch -D gh-pages',
        'git branch -rd origin/gh-pages',
        'git gc --aggressive --prune=now',
        'ghp-import -p build/html -n',
        'git push -f origin gh-pages',
    ]
    os.system(';'.join(cmds))

def clean():
    if os.path.exists('build'):
        shutil.rmtree('build')

def generate_rsts():
    """
    Prepare build/source.
    """
    from vbench.reports import generate_rst_files, generate_rst_analysis
    from suite import (
        benchmarks, DB_PATH, RST_BASE, DESCRIPTION, REPO_BROWSE, BRANCHES
    )

    os.system('rsync -a {0} build/'.format(RST_BASE))
    outpath = os.path.join('build', RST_BASE)
    generate_rst_analysis(
                   benchmarks,
                   dbpath=DB_PATH,
                   outpath=outpath,
                   gh_repo=REPO_BROWSE)
    generate_rst_files(benchmarks,
                   dbpath=DB_PATH,
                   outpath=outpath,
                   branches=BRANCHES,
                   description=DESCRIPTION + """

.. include:: analysis.rst

""")
    return outpath

def html():
    check_build()
    outpath = generate_rsts()
    cmd = 'sphinx-build -P -b html -d build/doctrees {0} build/html'
    if os.system(cmd.format(outpath)):
        raise SystemExit("Building HTML failed.")
    if os.system('touch build/html/.nojekyll'):
        raise SystemExit("Touching nojekyll file managed to fail.")

def check_build():
    build_dirs = [
        'build',
        'build/doctrees',
        'build/html',
        'build/plots',
        'build/_static',
        'build/_templates'
    ]
    for d in build_dirs:
        try:
            os.mkdir(d)
        except OSError:
            pass

def all():
    clean()
    html()
    upload()

funcd = {
    'update'   : update,
    'html'     : html,
    'clean'    : clean,
    'upload'   : upload,
    'all'      : all,
    }

small_docs = False

with cd(BASEDIR):
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            func = funcd.get(arg)
            if func is None:
                raise SystemExit('Invalid argument: {0}'.format(arg))
            else:
                func()
    else:
        small_docs = False
        all()
