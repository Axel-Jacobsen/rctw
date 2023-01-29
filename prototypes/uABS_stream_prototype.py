#! /usr/bin/env python3

import sys


from pathlib import Path
from math import log, floor, ceil
from typing import Dict, List, Tuple, Generator
from collections import defaultdict, OrderedDict

State = int
Symbol = int


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

    def D(self, x: State) -> Tuple[State, Symbol]:
        p = self.p1

        s = ceil((x + 1) * p) - ceil(x * p)

        if s == 0:
            xs = x - ceil(x * p)
        elif s == 1:
            xs = ceil(x * p)
        else:
            raise ValueError(f"got invalid value for s: {s}")

        return (xs, s)

    def C(self, x: State, s: Symbol) -> State:
        p = self.p1

        if s == 0:
            return ceil((x + 1) / (1 - p)) - 1
        elif s == 1:
            return floor(x / p)

        raise ValueError(f"got invalid value for s: {s}")


def get_Is(coder, I) -> Dict[Symbol, List[State]]:
    vs: List[Tuple[int, int]] = [coder.D(x) for x in I]

    d = defaultdict(list)

    for x, s in vs:
        d[s].append(x)

    return dict(d)


def stream_encode(input_stream, coder, I, b=2) -> Tuple[State, List[int]]:
    Iss = get_Is(coder, I)

    x = I[0]
    output_stream = []

    for s in input_stream:
        while x not in Iss[s]:
            output_stream.append(x % b)
            x /= b

        x = coder.C(x, s)
    return x, output_stream


def stream_decode(x, output_stream, coder, I, b=2) -> List[Symbol]:
    symbols = []
    while x > I[0]:
        x, s = coder.D(x)
        symbols.append(s)

        while x not in I:
            new_bit = output_stream.pop()
            x = x * b + new_bit

    return output_stream


if __name__ == "__main__":
    coder = uABS(0.3)

    seq = [1, 0, 0, 1, 0, 1, 0, 0]
    print(f"{seq=}")
    x, bitstream = stream_encode(seq, coder, range(9, 18))
    print(f"{x=}, {bitstream=}")
    print(f"{log(x, 2)=}")
    print(f"original size={len(seq)}")
    output_stream = stream_decode(x, bitstream, coder, range(9, 18), b=2)
    print(f"{output_stream=}")
