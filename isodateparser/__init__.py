# -*- coding: utf-8 -*-
import logging
import json

class Token(object):
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

class ISODateParser(object):

    def __init__(self, input):
        self._logger = logging.getLogger(__name__)

        self._state = {
            "start": {
                "year": None,
                "month": None,
                "day": None,
                "hours": None,
                "minutes": None,
                "seconds": None,
                "milliseconds": None
            },
            "end": {
                "year": None,
                "month": None,
                "day": None,
                "hours": None,
                "minutes": None,
                "seconds": None,
                "milliseconds": None
            }
        }
        self._which = "start"
        self._input = input
        self._tokenize()
        self._disambiguate()
        self._logger.debug(self._printTokens(self._tokens))
        self._parse()

    def _parse(self):
        self._logger.debug("Parse input: " + self._printTokensShort(self._tokens))
        buffer = list()
        for token in self._tokens:
            if token.type == "INTERVALSEPARATOR":
                self._parsePart(buffer)
                buffer = list()
                self._which = "end"
            else:
                buffer.append(token)
        self._parsePart(buffer)

    def _parsePart(self, tokens):
        self._logger.debug("Parse part: " + self._printTokensShort(tokens))
        for token in tokens:
            if token.type == "DATESEPARATOR" or token.type == "TIMESEPARATOR":
                return self._parseDateTime(tokens)
            elif token.type == "DESIGNATOR":
                return self._parseDuration(tokens)
        raise RuntimeError("No date separator or duration designator found")

    def _parseDateTime(self, tokens):
        self._logger.debug("Parse datetime: " + self._printTokensShort(tokens))
        buffer = list()
        time = False
        for token in tokens:
            if token.type == "DATETIMESEPARATOR":
                self._parseDate(buffer)
                time = True
                buffer = list()
            else:
                buffer.append(token)
        if (time):
            self._parseTime(buffer)
        else:
            self._parseDate(buffer)

    def _parseDate(self, tokens):
        self._logger.debug("Parse date: " + self._printTokensShort(tokens))
        state = 0
        for token in tokens:
            if token.type == "NUMBER":
                if (state == 0):
                    self._state[self._which]["year"] = int(token.value)
                    state += 1
                elif (state == 1):
                    self._state[self._which]["month"] = int(token.value)
                    state += 1
                elif (state == 2):
                    self._state[self._which]["day"] = int(token.value)

    def _parseTime(self, tokens):
        self._logger.debug("Parse time: " + self._printTokensShort(tokens))
        pass

    def _parseDuration(self, tokens):
        self._logger.debug("Parse duration: " + self._printTokensShort(tokens))
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
                    raise RuntimeError("Character " + c + " not recognized")

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
        lines.append(self._printTokens(self._tokens))
        lines.append(json.dumps(self._state))
        return "\n".join(lines)

    def _printTokens(self, tokens):
        lines = list()
        for token in tokens:
            line = token.type
            if token.value is not None:
                line += " (" + str(token.value) + ")"
            lines.append(line)
        return "\n".join(lines)

    def _printTokensShort(self, tokens):
        return "".join([token.value for token in tokens])