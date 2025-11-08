// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

contract BabyStore {
    struct Item {
        string name;
        string content;
        uint256 price;
        bool isFlag;
    }
    Item[] private items;

    mapping(address => Item[]) public itemsBought;

    constructor() payable {
        items.push(Item("Kebab", "Mums", 100 ether, false));
        items.push(Item("Flagga", "Omg on skibidi", 50 ether, true));
        items.push(Item("42", "42", 42 ether, false));
    }

    function buyItem(uint256 idx) public payable {
        require(idx < items.length, "Index out of bounds");
        require(msg.value >= items[idx].price, "Insufficient funds");

        itemsBought[msg.sender].push(items[idx]);
    }

    function hasFlag(address playerAddr) public view returns (bool) {
        for (uint256 i = 0; i < itemsBought[playerAddr].length; i++) {
            if (itemsBought[playerAddr][i].isFlag) {
                return true;
            }
        }
        return false;
    }
}
