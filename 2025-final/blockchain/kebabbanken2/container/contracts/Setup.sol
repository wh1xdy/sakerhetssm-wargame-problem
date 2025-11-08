// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

import "./KebabBanken2.sol";
contract Setup {
    KebabBanken2 public immutable bank;

    address public player = address(0);

    constructor() payable {
        bank = new KebabBanken2();
        bank.openAccount{value: 100 ether}("john pork hawk tuah");
    }

    function hello() public {
        player = msg.sender;
    }

    function isSolved() public view returns (bool) {
        require(player != address(0), "Player not set");
        return bank.checkBreach();
    }
}
