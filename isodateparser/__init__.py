# -*- coding: utf-8 -*-
import logging
import json
from calendar import monthrange
import datetime

class Token(object):
    def __init__(self, kind, value=None):
        self.kind = kind
        self.value = value

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
        pass

    # def _parse(self):
    #     state_primary = "start"
    #     state_secondary = "datetime"
    #     state_time = False
    #     previous_token = None
    #     for token in self._tokens:
    #         if token.kind == "DATESEPARATOR":
    #             if state_secondary not in "datetime":
    #                 raise ValueError("Unexpected token " + token.value)
    #             if previous_token is None or previous_token.kind != "NUMBER":
    #                 raise ValueError("Unexpected token " + token.value)
    #         elif token.kind == "TIMESEPARATOR":
    #             if state_secondary not in ("datetime", "timezone"):
    #                 raise ValueError("Unexpected token " + token.value)
    #             if previous_token is None or previous_token.kind != "NUMBER":
    #                 raise ValueError("Unexpected token " + token.value)
    #         elif token.kind == "DATETIMESEPARATOR":
    #             if state_secondary not in "datetime":
    #                 raise ValueError("Unexpected token " + token.value)
    #             if previous_token is None or previous_token.kind != "NUMBER":
    #                 raise ValueError("Unexpected token " + token.value)
    #         elif token.kind == "TIMEZONESIGN":
    #             if not state_time:
    #                 raise ValueError("Unexpected token " + token.value)
    #         if token.kind == "DATETIMESEPARATOR":
    #             state_time = True
    #         elif token.kind == "INTERVALSEPARATOR":
    #             state_primary = "end"
    #             state_secondary = "datetime"
    #             state_time = False
    #         elif token.kind == "PERIOD":
    #             state_secondary = "duration"
    #         elif token.kind == "TIMEZONESIGN":
    #             state_secondary = "timezone"
    #         elif token.kind == "UTC":
    #             state_secondary = "timezone"
    #         if token.kind in ("NUMBER", "DESIGNATOR", "TIMEZONESIGN", "UTC"):
    #             self._parsed[state_primary][state_secondary].append(token)
    #         previous_token = token
    #     self._shift(self._parsed)

    # def _populate(self):
    #     parts = ["year", "month", "day", "hours", "minutes", "seconds", "microseconds"]
    #     for i in ["start", "end"]:
    #         for j in range(len(self._parsed[i]["datetime"])):
    #             if self._parsed[i]["datetime"][j]:
    #                 value = self._parsed[i]["datetime"][j].value
    #             elif i == "end":
    #                 value = self._parsed["start"]["datetime"][j].value
    #             self.components[i][parts[j]] = int(value)
    #     for i in ["start", "end"]:
    #         state = 0
    #         hours = None
    #         minutes = 0.0
    #         sign = 1.0
    #         for token in self._parsed[i]["timezone"]:
    #             if token.kind == "UTC":
    #                 self.components[i]["timezone"] = 0.0
    #             elif token.kind == "TIMEZONESIGN" and token.value == "-":
    #                 sign = -1.0
    #             elif token.kind == "NUMBER":
    #                 if len(token.value) == 4:
    #                     hours = int(token.value[0:2])
    #                     minutes = int(token.value[2:4])
    #                 if len(token.value) == 2:
    #                     if state == 0:
    #                         hours = int(token.value)
    #                         state += 1
    #                     elif state == 1:
    #                         minutes = int(token.value)
    #         if hours is not None:
    #             self.components[i]["timezone"] = sign * (hours + minutes / 60.0)

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
                    self._tokens.append(Token("NUMBER", "".join(buffer)))
                    # todo: number of length 8 should be split into 4-2-2
                    buffer = list()
                if c == " " or c == "T":
                    self._tokens.append(Token("DATETIMESEPARATOR", c))
                elif c == ":":
                    self._tokens.append(Token("TIMESEPARATOR", c))
                elif c == "/":
                    self._tokens.append(Token("INTERVALSEPARATOR", c))
                elif c == "Z":
                    self._tokens.append(Token("UTC", c))
                elif c == "+":
                    self._tokens.append(Token("TIMEZONESIGN", c))
                elif c == "-" or c == "−":
                    self._tokens.append(Token("MINUS", c))
                elif c == "P":
                    self._tokens.append(Token("PERIOD", c))
                elif c in ["Y", "M", "W", "D", "H", "M", "S"]:
                    self._tokens.append(Token("DESIGNATOR", c))
                elif c == "R":
                    self._tokens.append(Token("REPEAT", c))
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
            if token.kind == "TIMESEPARATOR":
                time = True
            elif token.kind == "INTERVALSEPARATOR":
                time = False
            elif token.kind == "MINUS":
                if time:
                    self._tokens[i] = Token("TIMEZONESIGN", "-")
                else:
                    self._tokens[i] = Token("DATESEPARATOR", "-")

    def _print_tokens(self, tokens):
        lines = list()
        for token in tokens:
            line = token.kind
            if token.value is not None:
                line += " (" + str(token.value) + ")"
            lines.append(line)
        return "\n".join(lines)
