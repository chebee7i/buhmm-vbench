#!/usr/bin/env python
# coding: utf8

"""
Runs the benchmarks and saves the results.

"""

import logging, os, sys

BASEDIR = os.path.dirname(os.path.realpath(__file__))
# This allows us to import from the base folder.
sys.path.insert(0, BASEDIR)
sys.path.insert(0, os.path.join(BASEDIR, 'benchmarks'))

from vbench.api import BenchmarkRunner, verify_benchmarks
from vbench.config import is_interactive

import suite

log = logging.getLogger('vb')

def run_process(existing='min', run_order='multires', run_limit=None):
    runner = BenchmarkRunner(suite.benchmarks,
                             suite.REPO_PATH,
                             suite.REPO_URL,
                             suite.BUILD,
                             suite.DB_PATH,
                             suite.TMP_DIR,
                             suite.PREPARE,
                             branches=suite.BRANCHES,
                             clean_cmd=suite.PREPARE,
                             run_option='all',
                             run_order=run_order,
                             run_limit=run_limit,
                             start_date=suite.START_DATE,
                             existing=existing,
                             module_dependencies=suite.dependencies,
                             verify=True)
    runner.run()

if __name__ == '__main__':
    import sys

    if 'verify' in sys.argv:
        verify_benchmarks(suite.benchmarks, raise_=True)
    else:
        try:
            # quick pass through to get at least some results for only
            # new benchmarks and/or commits
            run_process(existing='skip', run_order='multires')
            # now a thorough pass through trying to get better
            # estimates for some of previous without running all of them
            run_process(existing='min', run_order='random', run_limit=100)
        except Exception as exc:
            log.error('%s (%s)' % (str(exc), exc.__class__.__name__))
            if __debug__ and is_interactive(): # and args.common_debug:
                import pdb
                pdb.post_mortem()
            raise

