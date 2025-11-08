export RPC=http://localhost:31337/51d3e09d-8771-4089-a83c-2ff85eeb7994
export PVKEY=0xeeee0ceb1ba3c1c5c73ba9b8d795c569057e89a6a1454ffd46c4b2cb3e3db026
export SETUP=0xB246609cF8d9a5E3fB75791f3D9ff5C8222128a6

forge script --broadcast --rpc-url $RPC --private-key $PVKEY ./Exploit.sol:Exploit --evm-version cancun

# If you get error "Error: Failure on receiving a receipt" - rerun this script with the "--resume" flag on the forge command
