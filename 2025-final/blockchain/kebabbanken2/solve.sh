export RPC=http://localhost:31337/eae3dddb-d302-4a77-902c-1f9f4761090d
export PVKEY=0x5b5188c3d1356918ff72d8f4d00b76b81ac40b482a50d0780617bf15e0a8c886
export SETUP=0x4E6a6D8a293eE0edEAbdA5CDaD97f9Bbb49497bf

forge script --broadcast --rpc-url $RPC --private-key $PVKEY ./Exploit.sol:Exploit --evm-version cancun