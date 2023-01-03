use std::env;
use std::fs::File;
use std::collections::HashMap;
use std::io::{BufReader, Read};

mod filechunker;
mod tANS;

const CHUNK_SIZE: usize = 2; // chunk size, bytes

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

fn symbol_freq<R: Read>(reader: BufReader<R>) -> HashMap<Vec<u8>, u64> {
    // TODO define type for this hashmap of symbols -> frequencies?
    let mut hm = HashMap::new();
    let file_chunker = filechunker::FileChunker::new(reader, CHUNK_SIZE);
    for chunk in file_chunker {
        match chunk {
            Ok(ch) => {
                // brackets because we gotta return none, and or_insert and
                // and_modify return values
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
    println!("{:?}", reader);

    let r = symbol_freq(reader);
    Ok(())
}
