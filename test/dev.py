import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from isodateparser import ISODateParser
import logging

logging.basicConfig(level=logging.DEBUG)

# 2017-08-24
# 2017-08-24T14:51:57+00:00
# 2017-08-24T14:51:57Z
# 20170824T145157Z
# 2017-W34
# 2017-W34-4
# 2017-236
# P3Y6M4DT12H30M5S
# 2007-03-01T13:00:00Z/P1Y2M10DT2H30M
# P1Y2M10DT2H30M/2008-05-11T15:30:00Z

parser = ISODateParser("1990-01-02T03:04:05/2014-05-06 07:08+0900")
print parser.components()
