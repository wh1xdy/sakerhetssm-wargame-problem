// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

import "./SL.sol";
contract Setup {
    SL public immutable sl;

    address public player = address(0);

    constructor() payable {
        sl = (new SL){value: 100 ether}();
        sl.setOperational(true);
    }

    function hello() public {
        player = msg.sender;
    }

    function isSolved() public view returns (bool) {
        require(player != address(0), "Player not set");
        return sl.owner() == player;
    }
}
