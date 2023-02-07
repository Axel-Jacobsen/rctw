import unittest

from coder import tANS


class TesttANS(unittest.TestCase):
    def test_basic_table_gen(self):
        freqs = {0: 10, 1: 5, 2: 2}
        coder = tANS(freqs, base=2, l=17)
        # table size should be twice 17, because our table stores k->v and v->k
        self.assertEqual(len(coder._table), 17 * 2)

    def test_table_gen_byte_transfer(self):
        freqs = {0: 10, 1: 5, 2: 2}
        coder = tANS(freqs, base=2 << 8, l=17)
        # table size should be twice 17, because our table stores k->v and v->k
        self.assertEqual(len(coder._table), 8687 * 2)


if __name__ == "__main__":
    unittest.main()
