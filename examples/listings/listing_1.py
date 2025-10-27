"""

mweigert@mpi-cbg.de
"""
from __future__ import print_function, unicode_literals, absolute_import, division

# make project root importable when running this example directly
# (ensures the top-level folder that contains the `biobeam` package
# is on sys.path)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from biobeam import focus_field_beam

# e.g. psf of a bessel beam with
# annulus 0.4<rho<0.45 in a volume
field = focus_field_beam(shape = (256,256,256),\
	units = (0.1,0.1, 0.1),NA = 0.4)