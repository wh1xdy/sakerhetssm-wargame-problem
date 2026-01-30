# Lottery

| Meta              | Value        |
|-------------------|--------------|
| **Category:**     | Reversing    |
| **Difficulty:**   | Easy         |
| **Author:**       | ZetaTwo      |
| **Technologies:** | Javscript    |

## Validation

To validate that the challenge is working correctly, start the container with `challtools start -b`, go to `http://localhost:50000/#3T1X9XS0J1W0Q38Z` and scratch the lottery ticket.

## Challenge Explanation

The challenge is basically a dressed up crackme. The web page will generate a random ticket ID for you and then you can scratch it to see if you won. Only one specific ticket ID will give you a win. The players will not hit this by random chance and must instead recover the target ticket ID from the validation logic.

## Intended Solution

By reading the Javascript code, the players can find the `validate` function. This function checks that the ticket ID is the expected length before XORing it with a constant value and comparing it to a target. By XORing the target with the constant value, the player can recover the ticket ID they need. They can then enter this into the site and scratch the ticket to get the flag.
