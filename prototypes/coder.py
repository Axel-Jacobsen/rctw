import abc
import heapq

from math import floor, ceil
from functools import lru_cache
from dataclasses import dataclass
from typing import Dict, Tuple, List


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
    you 31 which messes everything up. use rANS or tANS instead
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


class tANSTable:
    """
    It should look something like this:

    Table T[state, symbol] = next_state
    __________________________________________
    state, x | 17  18  19  20  21  22  23  ...
    s = 0    | 10      11      12      13
    s = 1    |      5               6
    s = 2    |              2
    __________________________________________

    T[17, 2] = 2
    T[21, 2] = 3
    T[23, 0] = 13

    TODO need a better name for this
    """

    def __init__(self):
        self.C_dict: Dict[Tuple[Symbol, State], State] = dict()
        self.D_dict: Dict[State, Tuple[Symbol, State]] = dict()

    def __repr__(self):
        return repr(self.C_dict)

    def set_range(self, symbol: Symbol, state_range: range, succeeding_state: State):
        for state in state_range:
            self.C_dict[(symbol, state)] = succeeding_state
            self.D_dict[succeeding_state] = (symbol, state)

    def encode(self, symbol: Symbol, state: State) -> State:
        return self.C_dict[(symbol, state)]

    def decode(self, state: State) -> Tuple[Symbol, State]:
        return self.D_dict[state]


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

    def __lt__(self, other: "ValuePair") -> bool:
        if self.value == other.value:
            return self.prob < other.prob
        return self.value < other.value


class tANS(Coder):
    def __init__(
        self, symbol_frequencies: Dict[Symbol, int], base: int = 8, l: int = 9
    ):
        self.freqs: Dict[Symbol, int] = symbol_frequencies
        self._total_num_symbols = sum(self.freqs.values())
        self._table = self._generate_table(base, l)

    def _generate_table(self, base: int, l: int) -> tANSTable:
        table: tANSTable = tANSTable()
        heap: List[ValuePair] = []

        for symbol, freq in self.freqs.items():
            prob = freq / self._total_num_symbols
            value = 1 / (2 * prob)
            xs = freq

            heapq.heappush(
                heap, ValuePair(symbol=symbol, state=xs, prob=prob, value=value)
            )

        prev_xs: Dict[Symbol, State] = {
            sym: l * self._total_num_symbols for sym in self.freqs
        }
        for state in range(
            l * self._total_num_symbols, base * l * self._total_num_symbols
        ):
            smallest_symbol = heapq.heappop(heap)
            table.set_range(
                smallest_symbol.symbol,
                range(prev_xs[smallest_symbol.symbol], state + 1),
                state,
            )
            heapq.heappush(heap, smallest_symbol.increment())
            prev_xs[smallest_symbol.symbol] = state

        return table

    def D(self, x: State) -> Tuple[Symbol, State]:
        return self._table.decode(x)

    def C(self, s: Symbol, x: State) -> State:
        return self._table.encode(s, x)


if __name__ == "__main__":
    t = tANS({0: 3, 1: 3, 2: 2}, base=2, l=1)
    for pair in sorted(list(t._table.C_dict.items()), key=lambda p: (p[0][1], p[0][0])):
        print(pair)
