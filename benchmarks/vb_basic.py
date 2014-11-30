# coding: utf8

from vbench.benchmark import Benchmark

setup = """
from __future__ import division

import buhmm
import cmpy

m = cmpy.machines.Even()
m.set_start_node('A')
data = m.symbols(1e6)

"""

code = """
x = buhmm.Infer(m, data)
"""

bm1 = Benchmark(code, setup, name='infer')
