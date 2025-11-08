// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

contract Secret {
    bool public solved = false;

    uint256 private omg = 0;
    uint256 private lol = 1000;
    uint256 private oh = 123123;

    uint256 private what = 0;

    function wow() public {
        omg += 1;
        what += 1;
    }

    function haha() public {
        lol -= omg;
        what += 1;
    }

    function hehe() internal {
        uint256 bababo = weee();
        require(bababo > 100, "bad...");
        require(bababo < 200, "bad......");
    }

    function weee() internal returns (uint256) {
        omg += 1;
        return block.number;
    }

    function solve(uint256 uhoh) public {
        hehe();
        require(omg == 42 && lol == 69, "no");
        require(oh == uhoh, "nooooo");
        require(what < 66, "nooooooooooo");
        solved = true;
    }
}
