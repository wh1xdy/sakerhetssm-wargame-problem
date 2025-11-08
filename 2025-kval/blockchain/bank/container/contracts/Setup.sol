// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

import "./KebabBanken.sol";
contract Setup {
    KebabBanken public immutable bank;

    address public player = address(0);

    constructor() payable {
        bank = new KebabBanken();
        bank.openAccount{value: 10 ether}("admin");
        bank.deposit{value: 90 ether}("skibidi");
    }

    function hello() public {
        player = msg.sender;
    }

    function isSolved() public view returns (bool) {
        require(player != address(0), "Player not set");
        return player.balance > 100 ether;
    }
}
