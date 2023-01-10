/*
 * ** tANS initialization **
 *
 * Assume we have l (total number of symbols), b (base for numeral system?), and
 * a probability distribution of n symbols: 0 < p_1,...,p_n < 1, \sum_s p_s = 1.
 *
 * Assume that probabilities are defined w/ 1/l accuracy (?)
 *
 * l_s := l * p_s \in \nats
 *
 * Encoding is defined by distributing symbols in a nearly-uniform way on
 *
 * I = {l, ..., bl - 1}
 *
 * - Will have (b - 1) * l_s = (b - 1) * l * p_s appearances of symbol s
 * - For every symbol s, eumerate its appearances by succeeding numbers from
 *
 * Is = {l_s, ..., b * l_s - 1}
 *
 * The challenge now is to find the optimal symbol distribution (i.e. make the table!)
 * Once could enumerate all possible distributions, but that would be (l choose
 * l_0,l_1,...,l_{n-1}) which is big. This is a fairly decend option, but it is not always
 * optimal.
 *
 * ** Algorithm for decent initialization **
 *
 * First define
 *
 * N_s := {1 / 2*ps + i / ps : i \in \nats}
 *
 * These n sets are uniformally distributed w/ the req'd densities, but
 * they are composed of real numbers, not natural numbers. To shift them
 * into natural numbers, pick min of all symbols
 *
 */

use std::cmp::Ordering;
use std::collections::BinaryHeap;
use std::collections::HashMap;
use std::ops::Range;

use std::io::Read;

use crate::filechunker;

#[allow(unused)]
// symbol used only for constructing the code table
#[derive(PartialEq)]
struct ValuePair<'a> {
    symbol: &'a Vec<u8>,
    prob: f64,
    value: f64,
    xs: u64,
}

fn value_pair_increment(vp: ValuePair) -> ValuePair {
    ValuePair {
        symbol: vp.symbol,
        prob: vp.prob,
        value: vp.value + 1f64 / vp.prob,
        xs: vp.xs + 1,
    }
}

// TODO why does this work?!?!
impl Eq for ValuePair<'_> {}

impl<'a> Ord for ValuePair<'a> {
    fn cmp(&self, other: &Self) -> Ordering {
        // BinaryHeap is, by default, a max heap.
        // We implement `cmp` so it is a min heap.
        // ValuePair is only used for this, so it is OK!
        // Not accounted for: NaN in float values
        if self.value < other.value {
            Ordering::Greater
        } else if self.value > other.value {
            Ordering::Less
        } else {
            if self.prob < other.prob {
                Ordering::Greater
            } else {
                Ordering::Less
            }
        }
    }
}

impl<'a> PartialOrd for ValuePair<'a> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

pub struct TableANSConfig {
    pub base: u64,
    pub total_num_symbols: u64,
    pub table_size: u64,
}

pub fn build_base_tans_config(symbol_freqs: &HashMap<Vec<u8>, u64>) -> TableANSConfig {
    // TODO make base and table size configurable - perhaps by command line,
    // perhaps by env vars.
    let base = 2 << 8;
    let total_num_symbols: u64 = symbol_freqs.values().fold(0, |acc, e| acc + *e);
    let table_size: u64 = 8 * total_num_symbols;

    TableANSConfig {
        base,
        table_size,
        total_num_symbols,
    }
}

pub fn generate_table<'a>(
    symbol_freqs: &'a HashMap<Vec<u8>, u64>,
    config: &TableANSConfig,
) -> HashMap<(&'a Vec<u8>, u64), u64> {
    let mut table = HashMap::new();
    let mut bh: BinaryHeap<ValuePair> = BinaryHeap::new();

    let total_num_symbols = config.total_num_symbols;
    let b = config.base; // per-byte readout :)
    let l = config.table_size;

    // init table
    for (symbol, freq) in symbol_freqs.iter() {
        let prob: f64 = (*freq as f64) / (total_num_symbols as f64);
        let value = 1. / (2. * prob);
        let xs = *freq;
        bh.push(ValuePair {
            symbol,
            prob,
            value,
            xs,
        })
    }

    for x in l..((b as u64) * l) {
        let smallest_symbol = bh.pop().unwrap();
        table.insert((smallest_symbol.symbol, smallest_symbol.xs), x);
        bh.push(value_pair_increment(smallest_symbol));
    }

    table
}

// pub fn encode<R: Read>(
pub fn encode(
    symbols: &Vec<Vec<u8>>,
    // file_chunker: filechunker::FileChunker<R>,
    code_table: HashMap<(&Vec<u8>, u64), u64>,
    config: TableANSConfig,
) {
    let mut x = config.table_size; // State! :)
    let valid_state_range = Range {
        start: config.table_size,
        end: config.base * config.table_size,
    };

    let mut symbol_counts: HashMap<Vec<u8>, u64> = HashMap::new();
    symbol_counts.insert(vec![b'0'], 9);
    symbol_counts.insert(vec![b'1'], 3);

    for symbol in symbols {
            // Ok(symbol) => {
                // brackets because we gotta return none, and or_insert and
                // and_modify return values
                let xs: &u64 = &symbol_counts.get(&symbol.to_vec()).unwrap();
                // let xs: &mut u64 = symbol_counts
                    // .entry(symbol.to_vec())
                    // .and_modify(|e| *e += 1)
                    // .or_insert(1);
                // weee reference and dereference and reference and ...
                println!("{:?}", (&symbol, *xs));
                println!("{:?}\n", code_table.get(&(&symbol, *xs)));
                symbol_counts
                    .entry(symbol.to_vec())
                    .and_modify(|e| *e += 1)
                    .or_insert(1);
            // }
            // Err(e) => panic!("error reading file: {:?}", e),
        }
}

#[cfg(test)]
mod t_ans_tests {
    use crate::t_ans::{generate_table, TableANSConfig, encode};
    use std::collections::HashMap;

    #[test]
    fn basic_table_gen() {
        let mut hm = HashMap::new();
        hm.insert(vec![0], 10);
        hm.insert(vec![1], 5);
        hm.insert(vec![2], 2);

        let test_config = TableANSConfig {
            base: 2,
            total_num_symbols: 3,
            table_size: 17,
        };

        let table = generate_table(&hm, &test_config);
        assert_eq!(table.len(), 17);
    }

    #[test]
    fn basic_table_gen_byte_transfer() {
        let mut hm = HashMap::new();
        hm.insert(vec![0], 10);
        hm.insert(vec![1], 5);
        hm.insert(vec![2], 2);

        let test_config = TableANSConfig {
            base: 2 << 8,
            total_num_symbols: 3,
            table_size: 17,
        };

        let table = generate_table(&hm, &test_config);
        assert_eq!(table.len(), 8687);
    }

    #[test]
    fn test_encode_basic() {
        let mut hm = HashMap::new();
        hm.insert(vec![b'0'], 9);
        hm.insert(vec![b'1'], 4);

        let test_config = TableANSConfig {
            base: 2,
            total_num_symbols: 2,
            table_size: 9,
        };

        let table = generate_table(&hm, &test_config);
        println!("{:?}", table);

        let v = vec![vec![b'1'], vec![b'0'], vec![b'0'], vec![b'1'], vec![b'0'], vec![b'1']];

        encode(&v, table, test_config);
    }
}
