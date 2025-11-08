// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

import "./Secret.sol";
contract Setup {
    Secret public immutable secret;

    address public player = address(0);

    constructor() payable {
        secret = new Secret();
    }

    function hello() public {
        player = msg.sender;
    }

    function secretMessage() public pure returns (string memory) {
        string memory message = "I found some intresting tools that could help:"
        " https://github.com/acuarica/evm and https://app.dedaub.com/decompile";

        return message;
    }

    function isSolved() public view returns (bool) {
        require(player != address(0), "Player not set");
        return secret.solved();
    }
}
