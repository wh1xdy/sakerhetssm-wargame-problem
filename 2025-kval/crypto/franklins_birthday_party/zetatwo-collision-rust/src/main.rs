use std::{collections::HashMap, time::Instant};
use sha2::{Digest, Sha256, digest::FixedOutput};

fn main() {
    let start = Instant::now();
    let mut hashes: HashMap<u64, u64> = HashMap::with_capacity(1 << 27);

    let mut candidate = 0;

    let mut hasher_base = Sha256::new();
    hasher_base.update(b"GIFFEL-");

    loop {
        let mut hasher = hasher_base.clone();
        hasher.update(format!("{candidate}").as_bytes());

        let digest = &hasher.finalize_fixed();
        let hashvalue = u64::from_be_bytes(digest[0..8].try_into().unwrap()); // 203 = 64+64+64 + 11
        let res = hashvalue >> 11;

        if hashes.contains_key(&res) {
            println!("Found collision!");
            println!("GIFFEL-{candidate}");
            println!("GIFFEL-{}", hashes.get(&res).unwrap());
            println!(
                "Time taken: {} seconds.",
                (Instant::now() - start).as_secs()
            );
            break;
        }

        hashes.insert(res, candidate);
        if candidate & 0x7FFFFF == 0 {
            println!("Progress: {candidate:#x}");
        }
        candidate += 1;
    }
}
