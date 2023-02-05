import abc
import heapq

from math import floor, ceil
from functools import lru_cache
from dataclasses import dataclass
from typing import Self, Dict, Tuple, List, Type, TypeVar, Generic


State = int
Symbol = int


class Coder(abc.ABC):
    @abc.abstractmethod
    def D(self, x: State) -> Tuple[Symbol, State]:
        ...

    @abc.abstractmethod
    def C(self, s: Symbol, x: State) -> State:
        ...


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


class rANS(Coder):
    def __init__(self, symbol_frequencies: Dict[Symbol, int]):
        self.freqs: Dict[Symbol, int] = symbol_frequencies

        # cache total freqs!
        self._m = sum(symbol_frequencies.values())

        self._bs = dict()

        s = 0
        for k in sorted(symbol_frequencies):
            self._bs[k] = s
            s += symbol_frequencies[k]

    @lru_cache(maxsize=512)
    def _s(self, x: State) -> Symbol:
        cumulative_sum = 0

        for i, k in enumerate(sorted(self.freqs)):
            cumulative_sum += self.freqs[k]
            if x < cumulative_sum:
                return k

        raise ValueError("couldn't do it")

    def C(self, s: Symbol, x: State) -> State:
        m = self._m
        li = self.freqs[s]
        bs = self._bs[s]

        return m * (x // li) + x % li + bs

    def D(self, x: State) -> Tuple[Symbol, State]:
        m = self._m
        s = self._s(x % m)

        li = self.freqs[s]
        bs = self._bs[s]

        return s, li * (x // m) + x % m - bs


T = TypeVar("T")
G = TypeVar("G")


class Table(dict, Generic[T, G]):
    "table class; given T != G, this is 'safe' from overwrites"

    def __setitem__(self, k: T, v: G):
        super().__setitem__(k, v)
        super().__setitem__(v, k)


@dataclass
class ValuePair:
    symbol: Symbol
    state: State
    prob: float
    value: float

    def increment(self):
        return ValuePair(
            symbol=self.symbol,
            state=self.state + 1,
            prob=self.prob,
            value=self.value + 1 / self.prob,
        )

    def __lt__(self, other: Self) -> bool:
        if self.value == other.value:
            return self.prob < other.prob
        return self.value < other.value


class tANS(Coder):
    def __init__(
        self, symbol_frequencies: Dict[Symbol, int], base: int = 8, l: int = 9
    ):
        self.freqs: Dict[Symbol, int] = symbol_frequencies
        self._table = self._generate_table(base, l)

    def _generate_table(self, base: int, l: int) -> Dict[Symbol, State]:
        table: Table[
            State | Tuple[Symbol, State], State | Tuple[Symbol, State]
        ] = Table()
        heap: List[ValuePair] = []
        total_num_symbols = sum(list(self.freqs.values()))

        # TODO time this vs. creating a list of ValuePairs and 'heapifying'
        for symbol, freq in self.freqs.items():
            prob = freq / total_num_symbols
            value = 1 / (2 * prob)
            xs = freq

            heapq.heappush(
                heap, ValuePair(symbol=symbol, state=xs, prob=prob, value=value)
            )

        for state in range(l, base * l):
            smallest_symbol = heapq.heappop(heap)
            table[(smallest_symbol.symbol, smallest_symbol.state)] = state
            heapq.heappush(heap, smallest_symbol.increment())

        return table

    def D(self, x: State) -> Tuple[Symbol, State]:
        return self._table[x]

    def C(self, s: Symbol, x: State) -> State:
        return self._table[(s, x)]


if __name__ == "__main__":
    t = tANS({0: 100, 1: 100})
    print(t._table)
