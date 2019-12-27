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
        text = "1990-01-02"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 1990)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], None)
        self.assertEqual(result["start"]["minutes"], None)
        self.assertEqual(result["start"]["seconds"], None)
        self.assertEqual(result["start"]["timezone"], None)
        self.assertEqual(result["end"]["year"], 1990)
        self.assertEqual(result["end"]["month"], 1)
        self.assertEqual(result["end"]["day"], 2)
        self.assertEqual(result["end"]["hours"], None)
        self.assertEqual(result["end"]["minutes"], None)
        self.assertEqual(result["end"]["seconds"], None)
        self.assertEqual(result["end"]["timezone"], None)

    def testSimpleDateTime(self):
        text = "1990-01-02T12:13:14"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 1990)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 12)
        self.assertEqual(result["start"]["minutes"], 13)
        self.assertEqual(result["start"]["seconds"], 14)
        self.assertEqual(result["start"]["timezone"], None)

    def testSimpleDateTimeSpace(self):
        text = "1990-01-02 12:13:14"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 1990)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 12)
        self.assertEqual(result["start"]["minutes"], 13)
        self.assertEqual(result["start"]["seconds"], 14)
        self.assertEqual(result["start"]["timezone"], None)

    def testDateRangeTimeZone(self):
        text = "1990-01-02T03:04:05/2014-05-06 07:08:09+0900"
        result = ISODateParser(text).components
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
        self.assertEqual(result["end"]["seconds"], 9)
        self.assertEqual(result["end"]["timezone"], 9)

    def testDateTimeUTC(self):
        text = "2017-08-24T14:51:57Z"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 2017)
        self.assertEqual(result["start"]["month"], 8)
        self.assertEqual(result["start"]["day"], 24)
        self.assertEqual(result["start"]["hours"], 14)
        self.assertEqual(result["start"]["minutes"], 51)
        self.assertEqual(result["start"]["seconds"], 57)
        self.assertEqual(result["start"]["timezone"], 0)

    def testTimeZoneWithSeparator(self):
        text = "2010-01-02T03:04+06:30"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["timezone"], 6.5)

    def testTimeZoneWithoutSeparator(self):
        text = "2010-01-02T03:04+0630"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["timezone"], 6.5)

    def testNegativeTimeZoneWithSeparator(self):
        text = "2010-01-02T03:04-06:30"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["timezone"], -6.5)

    def testNegativeTimeZoneWithoutSeparator(self):
        text = "2010-01-02T03:04-0630"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["start"]["day"], 2)
        self.assertEqual(result["start"]["hours"], 3)
        self.assertEqual(result["start"]["minutes"], 4)
        self.assertEqual(result["start"]["timezone"], -6.5)

    def testMonthRange(self):
        text = "2010-01/2012-05"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 2010)
        self.assertEqual(result["start"]["month"], 1)
        self.assertEqual(result["end"]["year"], 2012)
        self.assertEqual(result["end"]["month"], 5)

    def testDates(self):
        text = "1990-01/2014-05"
        result = ISODateParser(text).datetimes
        self.assertEqual(result["start"], datetime.datetime(1990, 1, 1, 0, 0, 0, 0))
        self.assertEqual(result["end"], datetime.datetime(2014, 5, 31, 23, 59, 59, 999999))

    def testDatesOnlyStart(self):
        text = "1990-01-02"
        result = ISODateParser(text).datetimes
        self.assertEqual(result["start"], datetime.datetime(1990, 1, 2, 0, 0, 0, 0))
        self.assertEqual(result["end"], datetime.datetime(1990, 1, 2, 23, 59, 59, 999999))
        self.assertEqual(result["mid"], datetime.datetime(1990, 1, 2, 12, 0, 0, 0))

    def testDatesOnlyMonth(self):
        text = "1990-01"
        result = ISODateParser(text).datetimes
        self.assertEqual(result["start"], datetime.datetime(1990, 1, 1, 0, 0, 0, 0))
        self.assertEqual(result["end"], datetime.datetime(1990, 1, 31, 23, 59, 59, 999999))

    def testBackSlash(self):
        text = "2003-04-30T12:00\\2003-04-30T17:30"
        with self.assertRaises(ValueError):
            ISODateParser(text)

    def testDashes(self):
        text = "--"
        with self.assertRaises(ValueError):
            ISODateParser(text)

    def testYearOmitted(self):
        text = "2008-02-15/03-14"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 2008)
        self.assertEqual(result["start"]["month"], 2)
        self.assertEqual(result["start"]["day"], 15)
        self.assertEqual(result["end"]["month"], 3)
        self.assertEqual(result["end"]["day"], 14)

    def testDateOmitted(self):
        text = "2018-03-01T05:06/07:08"
        result = ISODateParser(text).components
        self.assertEqual(result["start"]["year"], 2018)
        self.assertEqual(result["start"]["month"], 3)
        self.assertEqual(result["start"]["day"], 1)
        self.assertEqual(result["end"]["hours"], 7)
        self.assertEqual(result["end"]["minutes"], 8)

    def testTimeMissing(self):
        text = "1981-06-01+00:00"
        with self.assertRaises(ValueError):
            ISODateParser(text)

    def testImpossibleTimeValues(self):
        texts = ["2018-01-01T25:01:01", "2018-01-01T01:65:01", "2018-01-01T01:01:65"]
        for text in texts:
            with self.assertRaises(ValueError):
                ISODateParser(text)

    def testEndDay(self):
        text = "1973-06-18/26"
        parser = ISODateParser(text)
        result = parser.components
        self.assertEqual(result["start"]["year"], 1973)
        self.assertEqual(result["start"]["month"], 6)
        self.assertEqual(result["start"]["day"], 18)
        self.assertEqual(result["end"]["day"], 26)
        dates = parser.datetimes
        self.assertEqual(dates["start"], datetime.datetime(1973, 6, 18, 0, 0, 0, 0))
        self.assertEqual(dates["end"], datetime.datetime(1973, 6, 26, 23, 59, 59, 999999))

if __name__ == "__main__":
    unittest.main()