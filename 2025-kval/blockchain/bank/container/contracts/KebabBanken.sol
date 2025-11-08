// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.25;

contract KebabBanken {
    struct Transaction {
        string accountName;
        uint256 amount;
        string txIndentifier;
        bytes32 txHash;
    }

    bytes32[] public usedNames;
    mapping(address => string) public accountNames;

    Transaction[] public transactions;

    function openAccount(string memory name) public payable {
        require(bytes(name).length > 0, "Name cannot be empty");
        require(
            bytes(accountNames[msg.sender]).length == 0,
            "You already have an account"
        );
        for (uint256 i = 0; i < usedNames.length; i++) {
            require(
                keccak256(abi.encodePacked(name)) != usedNames[i],
                "Name already used"
            );
        }
        require(msg.value > 0, "Initial deposit required");

        accountNames[msg.sender] = name;
        usedNames.push(keccak256(abi.encodePacked(name)));

        string memory identifier = "initial_deposit";
        Transaction memory transaction = Transaction(
            name,
            msg.value,
            identifier,
            generateHash(name, identifier, msg.value)
        );
        transactions.push(transaction);
    }

    function deposit(string memory txIndentifier) public payable {
        require(
            bytes(accountNames[msg.sender]).length > 0,
            "Account not found"
        );

        Transaction memory transaction = Transaction(
            accountNames[msg.sender],
            msg.value,
            txIndentifier,
            generateHash(accountNames[msg.sender], txIndentifier, msg.value)
        );

        transactions.push(transaction);
    }

    function withdraw(string memory txIdentifier, uint256 amount) public {
        bytes32 txHash = generateHash(
            accountNames[msg.sender],
            txIdentifier,
            amount
        );
        for (uint256 i = 0; i < transactions.length; i++) {
            if (transactions[i].txHash == txHash) {
                uint256 txAmount = transactions[i].amount;
                delete transactions[i];
                payable(msg.sender).transfer(txAmount);
            }
        }
    }

    function generateHash(
        string memory name,
        string memory identifier,
        uint256 amount
    ) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(name, identifier, amount));
    }
}
