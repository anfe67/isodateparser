import unittest
import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from isodateparser import ISODateParser
import datetime

class Test(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def testSimpleDate(self):
        input = "1990-01-02"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 1990)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], None)
        self.assertEqual(result["start"]["minutes"], None)
        self.assertEqual(result["start"]["seconds"], None)
        self.assertEqual(result["start"]["timezone"], None)
        self.assertEqual(result["end"]["year"], None)
        self.assertEqual(result["end"]["month"], None)
        self.assertEqual(result["end"]["day"], None)
        self.assertEqual(result["end"]["hours"], None)
        self.assertEqual(result["end"]["minutes"], None)
        self.assertEqual(result["end"]["seconds"], None)
        self.assertEqual(result["end"]["timezone"], None)

    def testSimpleDateTime(self):
        input = "1990-01-02T12:13:14"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 1990)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 12)
        self.assertEqual(result["start"]["minutes"], 13)
        self.assertEqual(result["start"]["seconds"], 14)
        self.assertEqual(result["start"]["timezone"], None)

    def testSimpleDateTimeSpace(self):
        input = "1990-01-02 12:13:14"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 1990)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 12)
        self.assertEqual(result["start"]["minutes"], 13)
        self.assertEqual(result["start"]["seconds"], 14)
        self.assertEqual(result["start"]["timezone"], None)

    def testDateRangeTimeZone(self):
        input = "1990-01-02T03:04:05/2014-05-06 07:08+0900"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 1990)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["seconds"], 5)
        self.assertEqual(result["start"]["timezone"], None)
        self.assertEqual(result["end"]["year"], 2014)
        self.assertEqual(result["end"]["month"], 5)
        self.assertEqual(result["end"]["day"], 6)
        self.assertEqual(result["end"]["hours"], 7)
        self.assertEqual(result["end"]["minutes"], 8)
        self.assertEqual(result["end"]["seconds"], None)
        self.assertEqual(result["end"]["timezone"], 9)

    def testDateTimeUTC(self):
        input = "2017-08-24T14:51:57Z"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2017)
        self.assertEqual(result["start"]["month"], 8)
        self.assertEqual(result["start"]["day"], 24)
        self.assertEqual(result["start"]["hours"], 14)
        self.assertEqual(result["start"]["minutes"], 51)
        self.assertEqual(result["start"]["seconds"], 57)
        self.assertEqual(result["start"]["timezone"], 0)

    def testTimeZoneWithSeparator(self):
        input = "2010-01-02T03:04+06:30"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["timezone"], 6.5)

    def testTimeZoneWithoutSeparator(self):
        input = "2010-01-02T03:04+0630"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["timezone"], 6.5)

    def testNegativeTimeZoneWithSeparator(self):
        input = "2010-01-02T03:04-06:30"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["timezone"], -6.5)

    def testNegativeTimeZoneWithoutSeparator(self):
        input = "2010-01-02T03:04-0630"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["timezone"], -6.5)

    def testMonthRange(self):
        input = "2010-01/2012-05"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["end"]["year"], 2012)
        self.assertEqual(result["end"]["month"], 5)

    def testDates(self):
        input = "1990-01/2014-05"
        result = ISODateParser(input).dates
        self.assertEqual(result["start"], datetime.date(1990, 1, 1))
        self.assertEqual(result["end"], datetime.date(2014, 05, 31))

    def testDatesOnlyStart(self):
        input = "1990-01-02"
        result = ISODateParser(input).dates
        self.assertEqual(result["start"], datetime.date(1990, 1, 2))
        self.assertEqual(result["end"], datetime.date(1990, 1, 2))
        self.assertEqual(result["mid"], datetime.date(1990, 1, 2))

    def testDatesOnlyMonth(self):
        input = "1990-01"
        result = ISODateParser(input).dates
        self.assertEqual(result["start"], datetime.date(1990, 1, 1))
        self.assertEqual(result["end"], datetime.date(1990, 1, 31))

    def testBackSlash(self):
        input = "2003-04-30T12:00\\2003-04-30T17:30"
        with self.assertRaises(ValueError):
            ISODateParser(input).dates

    def testDashes(self):
        input = "--"
        with self.assertRaises(ValueError):
            ISODateParser(input).dates

    def testYearOmitted(self):
        input = "2008-02-15/03-14"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2008)
        self.assertEqual(result["start"]["month"], 2)
        self.assertEqual(result["start"]["day"], 15)
        self.assertEqual(result["end"]["month"], 3)
        self.assertEqual(result["end"]["day"], 14)

    def testDateOmitted(self):
        input = "2018-03-01T05:06/07:08"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2018)
        self.assertEqual(result["start"]["month"], 3)
        self.assertEqual(result["start"]["day"], 1)
        self.assertEqual(result["end"]["hours"], 7)
        self.assertEqual(result["end"]["minutes"], 8)

    def testDateOmitted2(self):
        input = "2018-03-01T05:06/T07:08"
        result = ISODateParser(input).components
        self.assertEqual(result["start"]["year"], 2018)
        self.assertEqual(result["start"]["month"], 3)
        self.assertEqual(result["start"]["day"], 1)
        self.assertEqual(result["end"]["hours"], 7)
        self.assertEqual(result["end"]["minutes"], 8)

    def testTimeMissing(self):
        input = "1981-06-01+00:00"
        with self.assertRaises(ValueError):
            ISODateParser(input).dates

if __name__ == "__main__":
    unittest.main()