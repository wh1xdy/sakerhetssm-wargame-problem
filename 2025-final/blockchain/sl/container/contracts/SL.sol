// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

interface Passenger {
    function offerPrice() external view returns (uint256);
    function confirmPurchase(bytes32 ticketIdentifier) external;
}

contract SL {
    uint256 public ticketPrice = 2 ether;

    uint256 public ticketsSold = 0;
    uint256 public maxTickets = 20;
    uint256 public timesBribed = 0;
    bool public isOperational = false;

    struct Ticket {
        bytes32 ticketIdentifier;
        bool used;
    }

    mapping(address => Ticket[]) public ticketsPurchased;

    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier operational() {
        require(isOperational, "SL is not operational");
        _;
    }

    constructor() payable {
        owner = msg.sender;
    }

    function setOperational(bool yes) public onlyOwner {
        isOperational = yes;
    }

    function buyTicket() public payable operational {
        Passenger passenger = Passenger(msg.sender);
        uint256 offeredPrice = passenger.offerPrice();

        if (offeredPrice >= ticketPrice) {
            if (ticketsSold > maxTickets) {
                require(
                    offeredPrice >= ticketPrice * (timesBribed + 2),
                    "Too many tickets sold, you must bribe me to get a ticket"
                );
                timesBribed++;
            }
            completePurchase(msg.sender);
        } else {
            revert("Insufficient ticket price offered");
        }
    }

    function completePurchase(address passengerAddress) internal {
        Passenger passenger = Passenger(passengerAddress);
        uint256 confirmedPrice = passenger.offerPrice();
        require(msg.value == confirmedPrice, "Incorrect payment amount");

        bytes32 ticketIdentifier = keccak256(
            abi.encodePacked(
                passengerAddress,
                confirmedPrice,
                block.timestamp,
                ticketsPurchased[passengerAddress].length
            )
        );

        Ticket memory ticket = Ticket(ticketIdentifier, false);

        ticketsPurchased[passengerAddress].push(ticket);

        passenger.confirmPurchase(ticketIdentifier);
        ticketsSold++;
    }

    function ride(bytes32 ticketIdentifier) public operational {
        bool hasValidTicket = false;

        for (uint256 i = 0; i < ticketsPurchased[msg.sender].length; i++) {
            if (
                ticketsPurchased[msg.sender][i].ticketIdentifier ==
                ticketIdentifier
            ) {
                if (!ticketsPurchased[msg.sender][i].used) {
                    ticketsPurchased[msg.sender][i].used = true;
                    hasValidTicket = true;
                    break;
                }
            }
        }

        require(hasValidTicket, "No valid ticket found");
    }

    function refundTicket(bytes32 ticketIdentifier) public {
        for (uint256 i = 0; i < ticketsPurchased[msg.sender].length; i++) {
            if (
                ticketsPurchased[msg.sender][i].ticketIdentifier ==
                ticketIdentifier
            ) {
                require(
                    ticketsPurchased[msg.sender][i].used == false,
                    "Ticket has already been used"
                );

                ticketsPurchased[msg.sender][i].used = true;
                ticketsSold--;

                payable(msg.sender).transfer(ticketPrice / 2);
                return;
            }
        }
    }

    function buySL() public payable operational {
        require(msg.value >= 123 ether, "Insufficient funds");
        owner = msg.sender;
    }
}
