use std::collections::HashMap;
use std::env;
use std::fs::File;
use std::io::{BufReader, Read};

mod filechunker;
mod t_ans;

/* TODO
 * - Create a "symbol" type
 *   - just so we aren't always passing around &Vec<Vec<u8>>
 */

const CHUNK_SIZE: usize = 1; // chunk size, bytes

fn load_fd() -> std::io::Result<File> {
    let args: Vec<String> = env::args().collect();

    // TODO replace base_fname w/ err condition
    let base_fname = "src/main.rs".to_string();
    let fname = if args.len() == 1 {
        &base_fname
    } else {
        &args[1]
    };

    File::open(fname)
}

fn symbol_freq<R: Read>(reader: BufReader<R>, chunk_size: Option<usize>) -> HashMap<Vec<u8>, u64> {
    // TODO define type for this hashmap of symbols -> frequencies?
    let mut hm = HashMap::new();
    let cs = chunk_size.unwrap_or(CHUNK_SIZE);
    let file_chunker = filechunker::FileChunker::new(reader, cs);
    for chunk in file_chunker {
        match chunk {
            Ok(ch) => {
                hm.entry(ch).and_modify(|e| *e += 1).or_insert(1);
            }
            Err(e) => panic!("error reading file: {:?}", e),
        }
    }
    hm.shrink_to_fit();
    hm
}

fn main() -> std::io::Result<()> {
    let fd = load_fd()?;

    let reader = BufReader::new(fd);
    let symbol_freqs = symbol_freq(reader, Some(CHUNK_SIZE));

    let cfg = t_ans::build_base_tans_config(&symbol_freqs);
    let code_table = t_ans::generate_table(&symbol_freqs, &cfg);

    // TODO this is hacky, repeating  myself
    // either we gotta rewind fd (including bufreader?)
    // or make this str -> filechunker process ez
    let fd = load_fd()?;
    let reader = BufReader::new(fd);
    let file_chunker = filechunker::FileChunker::new(reader, CHUNK_SIZE);

    // t_ans::encode(file_chunker, code_table, cfg);

    Ok(())
}

#[cfg(test)]
mod main_tests {
    use crate::symbol_freq;
    use std::fs::File;
    use std::io::BufReader;

    #[test]
    fn basic_symbol_freq() {
        // file is 'ab\n'
        let fd = File::open("testfiles/a.txt").unwrap();
        let reader = BufReader::new(&fd);
        let r = symbol_freq(reader, Some(1));
        assert_eq!(r.len(), 3);

        let num_a = r.get(&vec![b'a']).unwrap();
        let num_b = r.get(&vec![b'b']).unwrap();
        let num_newline = r.get(&vec![b'\n']).unwrap();

        assert_eq!(*num_a, 1);
        assert_eq!(*num_b, 1);
        assert_eq!(*num_newline, 1);
    }

    #[test]
    fn basic_symbol_freq_chunk_of_2() {
        // file is 'ab\n'
        let fd = File::open("testfiles/a.txt").unwrap();
        let reader = BufReader::new(&fd);
        let r = symbol_freq(reader, Some(2));
        assert_eq!(r.len(), 2);

        let num_ab = r.get(&vec![b'a', b'b']).unwrap();
        let num_newline = r.get(&vec![b'\n']).unwrap();
        assert_eq!(*num_ab, 1);
        assert_eq!(*num_newline, 1);
    }
}
