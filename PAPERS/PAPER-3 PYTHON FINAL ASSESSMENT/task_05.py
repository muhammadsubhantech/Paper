# Task 05 - Expression Validator and Evaluator

import re


class Calculator:
    def __init__(self, expression):
        cleaned = re.sub(r"\s+", "", expression)
        self.tokens = re.findall(r"\d+|[()+*/-]", cleaned)
        self.position = 0

        # Check that no unsupported characters were left out.
        joined = "".join(self.tokens)
        if joined != cleaned:
            raise ValueError("Expression contains an invalid character")

    def current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def take(self):
        token = self.current()
        self.position += 1
        return token

    def expression(self):
        value = self.term()

        while self.current() in ("+", "-"):
            operator = self.take()
            next_value = self.term()

            if operator == "+":
                value += next_value
            else:
                value -= next_value

        return value

    def term(self):
        value = self.factor()

        while self.current() in ("*", "/"):
            operator = self.take()
            next_value = self.factor()

            if operator == "*":
                value *= next_value
            else:
                if next_value == 0:
                    raise ZeroDivisionError("Cannot divide by zero")
                value /= next_value

        return value

    def factor(self):
        token = self.current()

        if token == "-":
            self.take()
            return -self.factor()

        if token == "+":
            self.take()
            return self.factor()

        if token == "(":
            self.take()
            value = self.expression()

            if self.current() != ")":
                raise ValueError("Missing closing parenthesis")

            self.take()
            return value

        if token is not None and token.isdigit():
            self.take()
            return int(token)

        raise ValueError("Invalid expression")

    def calculate(self):
        if not self.tokens:
            raise ValueError("Expression is empty")

        answer = self.expression()

        if self.current() is not None:
            raise ValueError("Unexpected part at the end of expression")

        return answer


def calculate(expression):
    return Calculator(expression).calculate()


if __name__ == "__main__":
    print(calculate("-(3 + 2) * 4 + 18 / 3"))
