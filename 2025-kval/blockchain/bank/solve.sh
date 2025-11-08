export RPC=http://localhost:31337/697d9a6b-b2d0-44e2-80ab-7653e14be33d
export PVKEY=0x0907760fa5a8104c41936f7180617d7416cc91d4bdb7b1fa5eba831ea596653e
export SETUP=0x327d04e2A91A929B1545D2b9f791832791727C3B

forge script --broadcast --rpc-url $RPC --private-key $PVKEY ./Exploit.sol:Exploit --evm-version cancun