export RPC=http://localhost:31337/91ed12b4-05ca-4612-acfa-4f5c1f702e30
export PVKEY=0x32bd810c4257e1954ff4925209bdca2316573e84daf480837835643fb1fbf65c
export SETUP=0x8fD9528336c4CbFc1D228acF0C0c93a267010Db0

forge script --broadcast --rpc-url $RPC --private-key $PVKEY ./Exploit.sol:Loop --evm-version cancun

forge script --broadcast --rpc-url $RPC --private-key $PVKEY ./Exploit.sol:Exploit --evm-version cancun

# Kör detta för att få ut evm bytecode från "Secret" kontraktet:
# cast code <secret_addr> --rpc-url $RPC
# Det finns sedan decompilers som kan användas för att få ut solidity kod (https://app.dedaub.com/decompile är najs)
# Sedan är det bara att revva på!!

