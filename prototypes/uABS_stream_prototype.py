#! /usr/bin/env python3

import abc
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


class Coder(abc.ABC):
    @abc.abstractmethod
    def D(self, x: State) -> Tuple[State, Symbol]:
        ...

    @abc.abstractmethod
    def C(self, x: State, s: Symbol) -> State:
        ...


class uABS(Coder):
    def __init__(self, p1: float):
        assert 0 < p1 < 1
        self.p1 = p1

    def D(self, x: State) -> Tuple[Symbol, State]:
        p = self.p1

        s = ceil((x + 1) * p) - ceil(x * p)

        if s == 0:
            xs = x - ceil(x * p)
        elif s == 1:
            xs = ceil(x * p)
        else:
            raise ValueError(f"got invalid value for s: {s}")

        return (s, xs)

    def C(self, x: State, s: Symbol) -> State:
        p = self.p1

        if s == 0:
            return ceil((x + 1) / (1 - p)) - 1
        elif s == 1:
            return floor(x / p)

        raise ValueError(f"got invalid value for s: {s}")



def stream_encode(coder: Coder, input_seq: List[Symbol], F_0: int, F_1: int) -> Tuple[List[int], State]:
    "limited case of list of 0s and 1s, b=2"

    assert all(s in (0,1) for s in input_seq)

    M = F_0 + F_1

    # configurable, any in Z+
    l = 9

    # base, also configurable
    b = 2

    I = range(l * M, 2 * l * M - 1)
    I0 = range(l * F_0, 2 * l * F_0 - 1)
    I1 = range(l * F_1, 2 * l * F_1 - 1)
    Is = {0: I0, 1: I1}

    state = l * M  # I[0]

    output_stream: List[int] = []

    for symbol in input_seq:
        print(f"{state}", f"{symbol}")
        while state not in Is[symbol]:
            output_stream.append(state % b)
            state //= b
        state = coder.C(state, symbol)

    return output_stream, state


def stream_decode(coder: Coder, coded_seq: List[Symbol], init_state: State, F_0: int, F_1: int) -> List[Symbol]:
    "limited case of list of 0s and 1s, b=2"

    M = F_0 + F_1

    # configurable, any in Z+
    l = 9

    # base, also configurable
    b = 2

    I = range(l * M, 2 * l * M - 1)
    I0 = range(l * F_0, 2 * l * F_0 - 1)
    I1 = range(l * F_1, 2 * l * F_1 - 1)
    Is = {0: I0, 1: I1}

    final_state = l * M  # I[0]
    state = init_state

    decoded_stream: List[int] = []

    while state != final_state:
        symbol, state = coder.D(state)
        decoded_stream.append(symbol)

        while state not in I:
            state = state * b + coded_seq.pop()

    return decoded_stream



if __name__ == "__main__":
    coder = uABS(0.3)

    input_seq = [1,0,0,1,0,1]
    M = len(input_seq)
    F_1 = sum(input_seq)
    F_0 = M - F_1

    output_stream, fin_state = stream_encode(coder, input_seq, F_0, F_1)
    print(output_stream, fin_state)
    decoded = stream_decode(coder, output_stream, fin_state, F_0, F_1)
    print(f"{decoded=}")
