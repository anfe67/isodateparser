# -*- coding: utf-8 -*-
import logging
import json
from calendar import monthrange
import datetime
from enum import Enum, auto

class Token(object):
    def __init__(self, kind, value=None):
        self.kind = kind
        self.value = value

class States(Enum):
    BEGIN = auto()
    YEAR = auto()
    YEAR_SEP = auto()
    MONTH = auto()
    MONTH_SEP = auto()
    DAY = auto()

class Tokens(Enum):
    NUMBER = auto()
    DATETIMESEPARATOR = auto()
    TIMESEPARATOR = auto()
    INTERVALSEPARATOR = auto()
    UTC = auto()
    TIMEZONESIGN = auto()
    MINUS = auto()
    PERIOD = auto()
    DESIGNATOR = auto()
    REPEAT = auto()
    DATESEPARATOR = auto()

class ISODateParser(object):

    def __init__(self, text):
        self._logger = logging.getLogger(__name__)
        self.components = {
            "start": {
                "year": None,
                "month": None,
                "week": None,
                "yearday": None,
                "weekday": None,
                "day": None,
                "hour": None,
                "minute": None,
                "second": None,
                "microsecond": None,
                "timezone": None,
                "years": None,
                "months": None,
                "weeks": None,
                "days": None,
                "hours": None,
                "minutes": None,
                "seconds": None
            },
            "end": {
                "year": None,
                "month": None,
                "week": None,
                "yearday": None,
                "weekday": None,
                "day": None,
                "hour": None,
                "minute": None,
                "second": None,
                "microsecond": None,
                "timezone": None,
                "years": None,
                "months": None,
                "weeks": None,
                "days": None,
                "hours": None,
                "minutes": None,
                "seconds": None
            }
        }
        self.datetimes = {
            "start": None,
            "end": None
        }
        self._tokens = list()
        self._text = text
        self._tokenize()
        self._disambiguate()
        self._parse()
        #self._populate()
        #self._make_datetimes()
        self._logger.debug(self._print_tokens(self._tokens))

    def _parse(self):
        part = "start"
        state = States.BEGIN

        for token in self._tokens:

            if state == States.BEGIN:
                if token.kind == Tokens.NUMBER:
                    self.components[part]["year"] = token.value
                    state = States.YEAR
                    continue
                raise ValueError("Unexpected token: " + token.value)

            elif state == States.YEAR:
                if token.kind == Tokens.DATESEPARATOR:
                    state = States.YEAR_SEP
                    continue
                raise ValueError("Unexpected token: " + token.value)

            elif state == States.YEAR_SEP:
                if token.kind == Tokens.NUMBER:
                    self.components[part]["month"] = token.value
                    state = States.MONTH
                    continue
                raise ValueError("Unexpected token: " + token.value)



    # def _make_datetimes(self):
    #     for i in ("start", "end"):
    #         args = list()
    #         args.append(self.components[i]["year"])
    #         if self.components[i]["month"]:
    #             args.append(self.components[i]["month"])
    #         else:
    #             args.append(1 if i == "start" else 12)
    #         if self.components[i]["day"]:
    #             args.append(self.components[i]["day"])
    #         else:
    #             args.append(1 if i == "start" else monthrange(*args)[1])
    #         if self.components[i]["hours"]:
    #             args.append(self.components[i]["hours"])
    #         else:
    #             args.append(0 if i == "start" else 23)
    #         if self.components[i]["minutes"]:
    #             args.append(self.components[i]["minutes"])
    #         else:
    #             args.append(0 if i == "start" else 59)
    #         if self.components[i]["seconds"]:
    #             args.append(self.components[i]["seconds"])
    #         else:
    #             args.append(0 if i == "start" else 59)
    #         if self.components[i]["microseconds"]:
    #             args.append(self.components[i]["microseconds"])
    #         else:
    #             args.append(0 if i == "start" else 999999)
    #         self.datetimes[i] = datetime.datetime(*args)
    #     self.datetimes["mid"] = self.datetimes["start"] + (self.datetimes["end"] - self.datetimes["start"]) / 2

    # def _shift(self, components):
    #     diff = len(components["start"]["datetime"]) - len(components["end"]["datetime"])
    #     if diff > 0:
    #         components["end"]["datetime"] = [None] * diff + components["end"]["datetime"]

    def _tokenize(self):
        queue = list(self._text)
        queue.append("\n")
        buffer = list()
        self._tokens = list()
        while queue:
            c = queue.pop(0)
            if c.isdigit():
                buffer.append(c)
            else:
                if len(buffer) > 0:
                    self._tokens.append(Token(Tokens.NUMBER, "".join(buffer)))
                    # todo: number of length 8 should be split into 4-2-2
                    buffer = list()
                if c == " " or c == "T":
                    self._tokens.append(Token(Tokens.DATETIMESEPARATOR, c))
                elif c == ":":
                    self._tokens.append(Token(Tokens.TIMESEPARATOR, c))
                elif c == "/":
                    self._tokens.append(Token(Tokens.INTERVALSEPARATOR, c))
                elif c == "Z":
                    self._tokens.append(Token(Tokens.UTC, c))
                elif c == "+":
                    self._tokens.append(Token(Tokens.TIMEZONESIGN, c))
                elif c == "-" or c == "−":
                    self._tokens.append(Token(Tokens.MINUS, c))
                elif c == "P":
                    self._tokens.append(Token(Tokens.PERIOD, c))
                elif c in ["Y", "M", "W", "D", "H", "M", "S"]:
                    self._tokens.append(Token(Tokens.DESIGNATOR, c))
                elif c == "R":
                    self._tokens.append(Token(Tokens.REPEAT, c))
                elif c == "\n":
                    pass
                else:
                    raise ValueError("Unexpected character " + c)
                # todo: handle week date

    def __str__(self):
        lines = list()
        lines.append("Input: " + self._text)
        lines.append("Tokens:")
        lines.append(self._print_tokens(self._tokens))
        lines.append("Components:")
        lines.append(json.dumps(self.components, indent=4))
        return "\n".join(lines)

    def _disambiguate(self):
        time = False
        for i, token in enumerate(self._tokens):
            if token.kind == Tokens.TIMESEPARATOR:
                time = True
            elif token.kind == Tokens.INTERVALSEPARATOR:
                time = False
            elif token.kind == Tokens.MINUS:
                if time:
                    self._tokens[i] = Token(Tokens.TIMEZONESIGN, "-")
                else:
                    self._tokens[i] = Token(Tokens.DATESEPARATOR, "-")

    def _print_tokens(self, tokens):
        lines = list()
        for token in tokens:
            line = str(token.kind)
            if token.value is not None:
                line += " (" + str(token.value) + ")"
            lines.append(line)
        return "\n".join(lines)
