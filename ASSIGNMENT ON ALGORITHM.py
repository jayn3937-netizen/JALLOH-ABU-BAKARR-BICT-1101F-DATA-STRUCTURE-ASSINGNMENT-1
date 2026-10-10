"""
DCOMP320 - Data Structures and Algorithms
Assignment: Stacks Implementation

Reads mathematical expressions from input.txt, evaluates each one using
stacks (shunting-yard style, two stacks), and writes the results to
output.txt in the same format (results replace expressions, separators kept).
"""

import os
import re


# --------------------------------------------------------------------------
# 1. Stack class
# --------------------------------------------------------------------------
class Stack:
    """A simple LIFO stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


# --------------------------------------------------------------------------
# 2. Expression parsing and evaluation
# --------------------------------------------------------------------------
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "u-": 3}   # u- = unary minus
TOKEN_RE = re.compile(r"\s*(\d+\.?\d*|\.\d+|[-+*/()])")


DASHES = "-\u2010\u2011\u2012\u2013\u2014\u2015\u2212"   # hyphen, en/em dash, minus sign


def normalize(text):
    """Convert look-alike symbols (x, division sign, long dashes) to plain ASCII."""
    for d in DASHES[1:]:
        text = text.replace(d, "-")
    return text.replace("\u00d7", "*").replace("\u00f7", "/").replace("\ufeff", "")


def tokenize(expression):
    """Split an expression string into numbers, operators and parentheses."""
    tokens, pos = [], 0
    expression = normalize(expression).strip()
    while pos < len(expression):
        match = TOKEN_RE.match(expression, pos)
        if not match:
            raise ValueError(f"invalid character '{expression[pos:].strip()[:1]}'")
        tokens.append(match.group(1))
        pos = match.end()
        while pos < len(expression) and expression[pos].isspace():
            pos += 1
    return tokens


def apply_operator(operators, values):
    """Pop one operator and its operand(s), compute, push the result."""
    op = operators.pop()
    if op == "u-":
        if values.is_empty():
            raise ValueError("invalid expression")
        values.push(-values.pop())
        return
    if values.size() < 2:
        raise ValueError("invalid expression")
    right = values.pop()
    left = values.pop()
    if op == "+":
        values.push(left + right)
    elif op == "-":
        values.push(left - right)
    elif op == "*":
        values.push(left * right)
    elif op == "/":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        values.push(left / right)


def evaluate_expression(expression):
    """Evaluate an infix expression with +, -, *, /, parentheses and precedence."""
    tokens = tokenize(expression)
    if not tokens:
        raise ValueError("empty expression")

    values = Stack()      # operand stack
    operators = Stack()   # operator / parenthesis stack
    prev = None           # previous token, used to detect unary minus

    for tok in tokens:
        if re.fullmatch(r"\d+\.?\d*|\.\d+", tok):
            values.push(float(tok))
        elif tok == "(":
            operators.push(tok)
        elif tok == ")":
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators, values)
            if operators.is_empty():
                raise ValueError("mismatched parentheses")
            operators.pop()  # discard "("
        else:  # operator
            if tok == "-" and (prev is None or prev in "+-*/("):
                tok = "u-"
            elif tok == "+" and (prev is None or prev in "+-*/("):
                prev = tok
                continue  # unary plus: ignore
            if tok == "u-":
                operators.push(tok)   # prefix operator: never pops others
            else:
                while (not operators.is_empty()
                       and operators.peek() != "("
                       and PRECEDENCE[operators.peek()] >= PRECEDENCE[tok]):
                    apply_operator(operators, values)
                operators.push(tok)
        prev = tok if tok != "u-" else "-"

    while not operators.is_empty():
        if operators.peek() == "(":
            raise ValueError("mismatched parentheses")
        apply_operator(operators, values)

    if values.size() != 1:
        raise ValueError("invalid expression")
    return values.pop()


def format_result(value):
    """Show whole numbers without a decimal part (13 not 13.0)."""
    if value == int(value):
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".")


# --------------------------------------------------------------------------
# 3. File processing
# --------------------------------------------------------------------------
def is_separator(line):
    """A separator line contains only dashes (e.g. -----)."""
    s = normalize(line).strip()
    return len(s) >= 2 and set(s) == {"-"}


def find_input_file(name="input.txt"):
    """Look for the input file in the current folder, then next to this script."""
    if os.path.isfile(name):
        return os.path.abspath(name)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:                       # e.g. running inside a notebook
        script_dir = os.getcwd()
    candidate = os.path.join(script_dir, name)
    return candidate if os.path.isfile(candidate) else None


def process_file(input_path, output_path):
    # utf-8-sig removes the hidden BOM that Windows Notepad can add
    with open(input_path, "r", encoding="utf-8-sig") as f:
        lines = [ln.rstrip("\r\n") for ln in f]

    output_lines = []
    for line in lines:
        if is_separator(line):
            output_lines.append(line.strip())   # keep the separator exactly as written
        elif line.strip() == "":
            continue  # ignore blank lines
        else:
            try:
                output_lines.append(format_result(evaluate_expression(line)))
            except ZeroDivisionError:
                output_lines.append("Error: division by zero")
            except (ValueError, IndexError) as err:
                output_lines.append(f"Error: {err}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines) + "\n")
    return output_lines


def main():
    input_path = find_input_file("input.txt")
    if input_path is None:
        print("Error: input.txt was not found.")
        print("Place input.txt in the same folder as this program "
              "(or the folder you run it from) and try again.")
        return 1
    output_path = os.path.join(os.path.dirname(input_path), "OUTPUT.TXT")
    results = process_file(input_path, output_path)
    print(f"Done. {len(results)} lines written to {output_path}")
    return 0


if __name__ == "__main__":
    main()