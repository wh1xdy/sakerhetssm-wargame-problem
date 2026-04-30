#!/bin/bash
STATE=268272976131813441180931981161134343684
{
    echo "$STATE"
    # send next 100 bits
    for i in {1..100}; do
        echo 0
    done
} | nc dual-lcg-dbrg.ctf.wales 1337
