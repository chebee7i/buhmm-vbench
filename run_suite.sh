#/bin/sh
# This is necessary so that child processes can find vbench.
PYTHONPATH=$PWD/vbench:$PYTHONPATH python run_suite.py "$@"
