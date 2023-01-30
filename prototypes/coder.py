import abc

from math import floor, ceil
from typing import Dict, Tuple
from functools import lru_cache


State = int
Symbol = int


class Coder(abc.ABC):
    @abc.abstractmethod
    def D(self, x: State) -> Tuple[Symbol, State]:
        ...

    @abc.abstractmethod
    def C(self, s: Symbol, x: State) -> State:
        ...


class rANS(Coder):
    def __init__(self, symbol_frequencies: Dict[Symbol, int]):
        self.freqs: Dict[Symbol, int] = symbol_frequencies

        # cache total freqs!
        self._m = sum(symbol_frequencies.values())

        self._bs = dict()

        s = 0
        for k in sorted(symbol_frequencies):
            s += symbol_frequencies[k]
            self._bs[k] = s

    @lru_cache(maxsize=512)
    def _s(self, x: State) -> Symbol:
        s = 0
        for k in sorted(self.freqs):
            s += self.freqs[k]
            if x < s:
                return k - 1

        raise ValueError("couldn't do it")

    def C(self, s: Symbol, x: State) -> State:
        m = self._m
        li = self.freqs[s]
        bs = self._bs[s]

        return m * (x // li) + bs + x % li

    def D(self, x: State) -> Tuple[Symbol, State]:
        m = self._m
        s = self._s(x % m)

        li = self.freqs[s]
        bs = self._bs[s]

        return s, li * (x // m) + x % m - bs


class uABS(Coder):
    """This suffers from floating point arithmetic error!

    You will get intermediate values of e.g. 30.000000000000004
    that *should* be 30, which you take the ceil of which gives
    you 31 which messes everything up. No wonder why this wasn't
    working!
    """

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

    def C(self, s: Symbol, x: State) -> State:
        p = self.p1

        if s == 0:
            print((x + 1) / (1 - p))
            return ceil((x + 1) / (1 - p)) - 1
        elif s == 1:
            return floor(x / p)

        raise ValueError(f"got invalid value for s: {s}")
