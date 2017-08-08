class Token(object):
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

class ISODateParser(object):

    def __init__(self, input):
        self._input = input
        self._tokenize()
        self._disambiguate()

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
                    self._tokens.append(Token("TIMESEPARATOR"))
                elif c == ":":
                    self._tokens.append(Token("COLON"))
                elif c == "/":
                    self._tokens.append(Token("INTERVALSEPARATOR"))
                elif c == "Z":
                    self._tokens.append(Token("UTC"))
                elif c == "+":
                    self._tokens.append(Token("TIMEZONESIGN", "+"))
                elif c == "-" or c == "−":
                    self._tokens.append(Token("MINUS", c))
                elif c == "P":
                    self._tokens.append(Token("PERIOD"))
                elif c in ["Y", "M", "W", "D", "H", "M", "S"]:
                    self._tokens.append(Token("DESIGNATOR"))
                elif c == "R":
                    self._tokens.append(Token("REPEAT"))
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
                    self._tokens[i] = Token("DATESEPARATOR")

    def __str__(self):
        lines = list()
        lines.append("Input: " + self._input)
        for token in self._tokens:
            line = token.type
            if token.value is not None:
                line += " (" + str(token.value) + ")"
            lines.append(line)
        return "\n".join(lines)