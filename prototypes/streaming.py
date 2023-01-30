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
    coder: Coder,
    input_seq: List[Symbol],
    freqs: Dict[Symbol, int],
    l: int = 9,
    b: int = 2,
) -> Tuple[List[int], State]:
    M = sum(freqs.values())

    I = range(l * M, 2 * l * M - 1)
    Is = get_Is(coder, I)

    state = l * M

    output_stream: List[int] = []

    for symbol in input_seq:
        while state not in Is[symbol]:
            output_stream.append(state % b)
            state //= b
        state = coder.C(symbol, state)

    return output_stream, state


def stream_decode(
    coder: Coder,
    coded_seq: List[Symbol],
    init_state: State,
    freqs: Dict[Symbol, int],
    l: int = 9,
    b: int = 2,
) -> List[Symbol]:
    M = sum(freqs.values())

    I = range(l * M, 2 * l * M - 1)
    Is = get_Is(coder, I)

    final_state = l * M  # I[0]

    decoded_stream: List[int] = []
    state = init_state

    while state != final_state:
        symbol, state = coder.D(state)
        decoded_stream.append(symbol)

        while state not in I:
            state = state * b + coded_seq.pop()

    return decoded_stream


if __name__ == "__main__":
    import random

    freqs = {9: 3, 1: 3, 2: 2}
    coder = rANS(freqs)

    for k in freqs:
        for i in range(0, sum(freqs.values())):
            # C \circ D = D \circ C = id
            cond = coder.D(coder.C(k, i)) == (k, i)
            woopsies_string = f"{coder.D(coder.C(k, i))=} == {(k, i)=}"
            assert cond, woopsies_string

    vs = freqs.items()
    input_seq = random.choices([v[0] for v in vs], weights=[v[1] for v in vs], k=10)
    print(input_seq)

    output_stream, fin_state = stream_encode(coder, input_seq, freqs)
    decoded = stream_decode(coder, output_stream, fin_state, freqs)

    assert (
        input_seq == decoded[::-1]
    ), f"\n{input_seq=}\n{  decoded[::-1]=}\n{input_seq=}"
