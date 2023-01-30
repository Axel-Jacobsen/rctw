#! /usr/bin/env python3

import abc
import sys

from pathlib import Path
from math import log, floor, ceil
from typing import Dict, List, Tuple, Generator
from collections import defaultdict, OrderedDict

from coder import rANS, Coder, State, Symbol


def iter_over_file_bytes(p: str) -> Generator[int, None, None]:
    with open(p, "rb") as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                return
            for c in chunk:
                yield c


def get_Is(coder, I) -> Dict[int, List[int]]:
    vs: List[Tuple[int, int]] = [coder.D(x) for x in I]

    d = defaultdict(list)

    for s, x in vs:
        d[s].append(x)

    return dict(d)


def stream_encode(
    coder: Coder, input_seq: List[Symbol], F_0: int, F_1: int
) -> Tuple[List[int], State]:
    "limited case of list of 0s and 1s, b=2"

    assert all(s in (0, 1) for s in input_seq)

    M = F_0 + F_1

    # configurable, any in Z+
    l = 9

    # base, also configurable
    b = 2

    I = range(l * M, 2 * l * M - 1)
    I = range(9, 18)
    Is = get_Is(coder, I)

    state = l * M  # I[0]
    state = 9

    output_stream: List[int] = []

    for symbol in input_seq:
        while state not in Is[symbol]:
            output_stream.append(state % b)
            state //= b
        state = coder.C(state, symbol)

    return output_stream, state


def stream_decode(
    coder: Coder, coded_seq: List[Symbol], init_state: State, F_0: int, F_1: int
) -> List[Symbol]:
    "limited case of list of 0s and 1s, b=2"

    M = F_0 + F_1

    # configurable, any in Z+
    l = 9

    # base, also configurable
    b = 2

    I = range(9, 18)
    Is = get_Is(coder, I)

    final_state = l * M  # I[0]
    final_state = 9

    decoded_stream: List[int] = []
    state = init_state

    while state != final_state:
        symbol, state = coder.D(state)
        decoded_stream.append(symbol)

        while state not in I:
            state = state * b + coded_seq.pop()

    return decoded_stream


if __name__ == "__main__":
    freqs = {0: 3, 1: 3, 2: 2}
    coder = rANS(freqs)

    for i in range(0, sum(freqs.values())):
        assert coder.D(coder.C(0, i)) == (
            0,
            i,
        ), f"{i} {coder.C(0, i)=} {coder.D(coder.C(0, i))=}, {(0, i)=}"

    # input_seq = [0,1,0,2,2,0,2,1,2]
    # M = len(input_seq)
    # F_1 = sum(input_seq)
    # F_0 = M - F_1

    # output_stream, fin_state = stream_encode(coder, input_seq, F_0, F_1)
    # print(output_stream, fin_state)
    # decoded = stream_decode(coder, output_stream, fin_state, F_0, F_1)
    # print(f"{decoded=}")
