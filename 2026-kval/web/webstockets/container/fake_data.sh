#!/usr/bin/env bash
set -euo pipefail

### Simulate real-time data
### Updates numbers in the feeds/*.json in a 1-2 second interval

feed_files=("/feeds/lsoc.json" "/feeds/shfe.json" "/feeds/soxxe.json" "/feeds/xnas.json")

random_feed=${feed_files[RANDOM % ${#feed_files[@]}]} # isnt bash beautiful? <3

random_value=$RANDOM

jq ".price |= $RANDOM" $random_feed > $random_feed.tmp && mv $random_feed.tmp $random_feed

jq ".delta |= $((RANDOM % 200 - 100))" $random_feed > $random_feed.tmp && mv $random_feed.tmp $random_feed

echo "crontab be workin" > /tmp/$RANDOM
