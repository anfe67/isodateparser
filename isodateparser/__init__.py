# -*- coding: utf-8 -*-
import logging
import json
import calendar
import datetime

class Token(object):
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

class ISODateParser(object):

    def __init__(self, text):
        self._logger = logging.getLogger(__name__)

        self.dates = {
            "start": None,
            "mid": None,
            "end": None
        }
        self.components = {
            "start": {
                "year": None,
                "month": None,
                "day": None,
                "hours": None,
                "minutes": None,
                "seconds": None,
                "milliseconds": None,
                "timezone": None
            },
            "end": {
                "year": None,
                "month": None,
                "day": None,
                "hours": None,
                "minutes": None,
                "seconds": None,
                "milliseconds": None,
                "timezone": None
            }
        }
        self._which = "start"
        self._input = text
        self._tokenize()
        self._disambiguate()
        self._logger.debug(self._print_tokens(self._tokens))
        self._parse()
        self._make_dates()

    def _parse(self):
        self._logger.debug("Parse input: " + self._print_tokens_short(self._tokens))
        buffer = list()
        for token in self._tokens:
            if token.type == "INTERVALSEPARATOR":
                self._parse_part(buffer)
                buffer = list()
                self._which = "end"
            else:
                buffer.append(token)
        self._parse_part(buffer)

    def _parse_part(self, tokens):
        self._logger.debug("Parse part: " + self._print_tokens_short(tokens))
        for token in tokens:
            if token.type == "DATESEPARATOR" or token.type == "TIMESEPARATOR":
                return self._parse_date_time(tokens)
            elif token.type == "DESIGNATOR":
                return self._parse_duration(tokens)
        # not separator, assuming year only
        return self._parse_date_time(tokens)

    def _parse_date_time(self, tokens):
        self._logger.debug("Parse datetime: " + self._print_tokens_short(tokens))
        buffer = list()
        time = False
        for token in tokens:
            if token.type == "DATETIMESEPARATOR":
                self._parse_date(buffer)
                time = True
                buffer = list()
            else:
                if token.type == "TIMESEPARATOR":
                    time = True
                buffer.append(token)
        if time:
            self._parse_time_timezone(buffer)
        else:
            self._parse_date(buffer)

    def _parse_date(self, tokens):
        self._logger.debug("Parse date: " + self._print_tokens_short(tokens))

        numbers = []

        for token in tokens:
            if token.type == "NUMBER":
                numbers.append(token.value)

        if self._which == "start" and len(numbers) == 0:
            raise ValueError("No year in date")

        state = 0
        if self._which == "end":
            if self.components["start"]["day"] is not None:
                if len(numbers) == 3:
                    state = 0
                elif len(numbers) == 2:
                    state = 1
                elif len(numbers) == 1:
                    state = 2
            elif self.components["start"]["month"] is not None:
                if len(numbers) == 2:
                    state = 0
                elif len(numbers) == 1:
                    state = 1

        for number in numbers:
            if state == 0:
                if len(number) != 4:
                    raise ValueError("No year in date")
                self.components[self._which]["year"] = int(number)
                state += 1
            elif state == 1:
                self.components[self._which]["month"] = int(number)
                state += 1
            elif state == 2:
                self.components[self._which]["day"] = int(number)

    def _parse_time_timezone(self, tokens):
        self._logger.debug("Parse time and timezone: " + self._print_tokens_short(tokens))
        buffer = list()
        timezone = False
        for token in tokens:
            if token.type == "TIMEZONESIGN" or token.type == "UTC":
                self._parse_time(buffer)
                timezone = True
                buffer = list()
            buffer.append(token)
        if timezone:
            self._parse_timezone(buffer)
        else:
            self._parse_time(buffer)

    def _parse_time(self, tokens):
        self._logger.debug("Parse time: " + self._print_tokens_short(tokens))
        state = 0
        for token in tokens:
            if token.type == "NUMBER":
                if state == 0:
                    if int(token.value) > 23:
                        raise ValueError("Impossible hours value: " + token.value)
                    self.components[self._which]["hours"] = int(token.value)
                    state += 1
                elif state == 1:
                    if int(token.value) > 59:
                        raise ValueError("Impossible minutes value: " + token.value)
                    self.components[self._which]["minutes"] = int(token.value)
                    state += 1
                elif state == 2:
                    if int(token.value) > 59:
                        raise ValueError("Impossible seconds value: " + token.value)
                    self.components[self._which]["seconds"] = int(token.value)
            elif token.type != "TIMESEPARATOR":
                raise ValueError("Time includes unexpected character " + token.value)

    def _parse_timezone(self, tokens):
        self._logger.debug("Parse timezone: " + self._print_tokens_short(tokens))
        state = 0
        hours = None
        minutes = 0.0
        sign = 1.0
        for token in tokens:
            if token.type == "UTC":
                self.components[self._which]["timezone"] = 0
            elif token.type == "TIMEZONESIGN" and token.value == "-":
                sign = -1.0
            elif token.type == "NUMBER":
                if len(token.value) == 4:
                    hours = int(token.value[0:2])
                    minutes = int(token.value[2:4])
                if len(token.value) == 2:
                    if state == 0:
                        hours = int(token.value)
                        state += 1
                    elif state == 1:
                        minutes = int(token.value)
        if hours is not None:
            self.components[self._which]["timezone"] = sign * (hours + minutes / 60.0)

    def _parse_duration(self, tokens):
        self._logger.debug("Parse duration: " + self._print_tokens_short(tokens))
        pass

    def _tokenize(self):
        queue = list(self._input)
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

    def _disambiguate(self):
        time = False
        for i, token in enumerate(self._tokens):
            if token.type == "TIMESEPARATOR":
                time = True
            elif token.type == "INTERVALSEPARATOR":
                time = False
            elif token.type == "MINUS":
                if time:
                    self._tokens[i] = Token("TIMEZONESIGN", "-")
                else:
                    self._tokens[i] = Token("DATESEPARATOR", "-")

    def __str__(self):
        lines = list()
        lines.append("Input: " + self._input)
        lines.append(self._print_tokens(self._tokens))
        lines.append(json.dumps(self.components))
        return "\n".join(lines)

    def _print_tokens(self, tokens):
        lines = list()
        for token in tokens:
            line = token.type
            if token.value is not None:
                line += " (" + str(token.value) + ")"
            lines.append(line)
        return "\n".join(lines)

    def _print_tokens_short(self, tokens):
        return "".join([token.value for token in tokens])

    def _start_date(self):
        year = self.components["start"]["year"]
        if "month" in self.components["start"] and self.components["start"]["month"] is not None:
            month = self.components["start"]["month"]
        else:
            month = 1
        if "day" in self.components["start"] and self.components["start"]["day"] is not None:
            day = self.components["start"]["day"]
        else:
            day = 1
        return datetime.date(year, month, day)

    def _end_date(self):
        if "year" in self.components["end"] and self.components["end"]["year"] is not None:
            year = self.components["end"]["year"]
        else:
            year = self.components["start"]["year"]
        if "month" in self.components["end"] and self.components["end"]["month"] is not None:
            month = self.components["end"]["month"]
        elif "month" in self.components["start"] and self.components["start"]["month"] is not None:
            month = self.components["start"]["month"]
        else:
            month = 12
        if "day" in self.components["end"] and self.components["end"]["day"] is not None:
            day = self.components["end"]["day"]
        elif "day" in self.components["start"] and self.components["start"]["day"] is not None:
            day = self.components["start"]["day"]
        else:
            day = calendar.monthrange(year, month)[1]
        return datetime.date(year, month, day)

    def _make_dates(self):
        self.dates["start"] = self._start_date()
        self.dates["end"] = self._end_date()
        self.dates["mid"] = self.dates["start"] + (self.dates["end"] - self.dates["start"]) / 2

    def components(self):
        return self.components