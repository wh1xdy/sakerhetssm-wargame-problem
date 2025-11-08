// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

import "./BabyStore.sol";
contract Setup {
    BabyStore public immutable store;

    address public player = address(0);

    constructor() payable {
        store = new BabyStore();
    }

    function hello() public {
        player = msg.sender;
    }

    // När denna funktion returnerar true så kan du hämta flaggan
    function isSolved() public view returns (bool) {
        require(player != address(0), "Player not set");
        return store.hasFlag(player);
    }
}
