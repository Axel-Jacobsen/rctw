#! /usr/bin/env python3

import sys


from pathlib import Path
from math import log, floor
from typing import List, Tuple, Generator
from collections import defaultdict, OrderedDict

""" testing rABS
"""


def iter_over_file_bytes(p: str) -> Generator[int, None, None]:
    with open(p, "rb") as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                return
            for c in chunk:
                yield c


def symbol_freqs(p: str) -> OrderedDict[int, int]:
    d: defaultdict[int, int] = defaultdict(int)
    for s in iter_over_file_bytes(p):
        d[s] += 1
    return OrderedDict(sorted(d.items()))


def get_symb(v, d: OrderedDict[int, int]):
    acc = 0
    for s, li in d.items():
        acc += li
        if acc > v:
            return s
    raise ValueError(f"no valid value found")


def D(x: int, d: OrderedDict[int, int], m) -> Tuple[int, int]:
    s = get_symb(x % m, d)
    ls = d[s]
    bs = sum([v for v in d if v < s])
    xs = ls * floor(x / m) + (x % m) - bs
    return (s, xs)


def C(s: int, x: int, d: OrderedDict[int, int], m) -> int:
    ls = d[s]
    bs = sum([v for v in d if v < s])
    return m * floor(x / ls) + bs + (x % ls)


def get_Is(s, I, d: OrderedDict[int, int], m) -> List[int]:
    return list(D(i, d, m)[1] for i in I)


def stream_encode(x: int, d: OrderedDict[int, int], m) -> Tuple[int, int]:
    pass


def base_attempt():
    freqs = symbol_freqs(sys.argv[1])

    num_chars = sum([v for v in freqs.values()])

    print(f"{num_chars=}")
    print(f"{len(freqs)=}")
    print(f"{freqs=}")

    x = 9
    for s in iter_over_file_bytes(sys.argv[1]):
        x = C(s, x, freqs, num_chars)

    print("coded", x)
    print("rough size", log(x, 2))
    print("------------")

    while x > 0:
        s, x = D(x, freqs, num_chars)
        print(chr(s), end="")

    print("\n------------")
    print("done")
