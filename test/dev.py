import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from isodateparser import ISODateParser
import logging
import json
from time import sleep

logging.basicConfig(level=logging.DEBUG)

#input = "2017-08-24"
#input = "2017-08-24T14:51:57+00:00"
#input = "2017-08-24T14:51:57Z"
#input = "20170824T145157Z"
#input = "2017-W34"
#input = "2017-W34-4"
#input = "2017-236"
#input = "P3Y6M4DT12H30M5S"
#input = "2007-03-01T13:00:00Z/P1Y2M10DT2H30M"
#input = "P1Y2M10DT2H30M/2008-05-11T15:30:00Z"
#input = "1990-01-02T03:04:05/2014-05-06 07:08+0900"
#input = "1990-01/2014-05"
#input = "1990-01"
#input = "1990"
#input = "--"
input = "2018-03-01T05:06/07:08"

parser = ISODateParser(input)
sleep(0.5)
print json.dumps(parser.components, indent=4, sort_keys=True)
print parser.dates
