use std::io::Read;

pub struct FileChunker<R> {
    reader: R,
    word_chunksize: usize,
}

impl<R: Read> FileChunker<R> {
    pub fn new(reader: R, word_chunksize: usize) -> Self {
        FileChunker {
            reader,
            word_chunksize,
        }
    }
}

impl<R: Read> Iterator for FileChunker<R> {
    type Item = std::io::Result<Vec<u8>>;

    fn next(&mut self) -> Option<Self::Item> {
        let mut contents = Vec::with_capacity(self.word_chunksize);
        match self
            .reader
            .by_ref()
            .take(self.word_chunksize as u64)
            .read_to_end(&mut contents)
        {
            Ok(fill_size) => {
                if fill_size > 0 {
                    Some(Ok(contents))
                } else {
                    None
                }
            }
            Err(e) => Some(Err(e)),
        }
    }
}
