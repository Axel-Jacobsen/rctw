#! /usr/bin/env python3

import sys


from pathlib import Path
from math import log, floor, ceil
from typing import List, Tuple, Generator
from collections import defaultdict, OrderedDict


def iter_over_file_bytes(p: str) -> Generator[int, None, None]:
    with open(p, "rb") as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                return
            for c in chunk:
                yield c


class uABS:
    def __init__(self, p1: float):
        assert 0 < p1 < 1
        self.p1 = p1

    def D(self, x) -> Tuple[int, int]:
        p = self.p1

        s = ceil((x + 1) * p) - ceil(x * p)

        if s == 0:
            xs = x - ceil(x * p)
        elif s == 1:
            xs = ceil(x * p)
        else:
            raise ValueError(f"got invalid value for s: {s}")

        return (xs, s)

    def C(self, x, s) -> int:
        p = self.p1

        if s == 0:
            return ceil((x + 1) / (1 - p)) - 1
        elif s == 1:
            return floor(x / p)

        raise ValueError(f"got invalid value for s: {s}")


class uABS2:
    def __init__(self, p1: float):
        assert 0 < p1 < 1
        self.p1 = p1

    def D(self, x) -> Tuple[int, int]:
        p = self.p1

        s = floor((x + 1) * p) - floor(x * p)

        if s == 0:
            xs = x - floor(x * p)
        elif s == 1:
            xs = floor(x * p)
        else:
            raise ValueError(f"got invalid value for s: {s}")

        return (xs, s)

    def C(self, x, s) -> int:
        p = self.p1

        if s == 0:
            return floor(x / (1 - p))
        elif s == 1:
            return ceil((x + 1) / p) - 1

        raise ValueError(f"got invalid value for s: {s}")


def enc_dec(coder):
    seq = [1, 0, 0, 1, 0, 1, 0, 0]
    expecting = [3, 5, 8, 26, 38, 128, 184, 264]
    x = 1
    ss = []
    for s, expected in zip(seq, expecting):
        x = coder.C(x, s)
        ss.append(s)
        print(f"got {x} expected {expected}")

    print(ss)

    ss = []
    while x > 1:
        xs, s = coder.D(x)
        x = xs
        ss.append(s)

    print(ss[::-1])

if __name__ == "__main__":

    coder = uABS(0.3)

    enc_dec(coder)

    coder2 = uABS2(0.3)

    enc_dec(coder2)
