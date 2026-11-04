"""Minimal S-expression reader for KiCad netlists (spike)."""
import re


def parse(text: str) -> list:
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack: list[list] = [[]]
    for t in toks:
        if t == "(":
            stack.append([])
        elif t == ")":
            done = stack.pop()
            stack[-1].append(done)
        else:
            stack[-1].append(t[1:-1] if t.startswith('"') else t)
    return stack[0][0]


def find(node: list, key: str) -> list:
    return [x for x in node if isinstance(x, list) and x and x[0] == key]
