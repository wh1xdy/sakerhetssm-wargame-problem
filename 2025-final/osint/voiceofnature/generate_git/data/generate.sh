#!/bin/bash

whoami

apt-get update
apt-get install -y git make gcc

cd $(mktemp -d); git clone https://github.com/wolfcw/libfaketime.git; cd libfaketime/src; make install

# date --set="2 OCT 2006 18:00:00"

cd /data

export LD_PRELOAD=/usr/local/lib/faketime/libfaketime.so.1
export FAKETIME_NO_CACHE=1

rm -rf /data/myrepo
git config --global user.name VoiceOfNature
git config --global user.email voiceofnature@penguinmail.com

export FAKETIME="2020-11-02 23:01:29"
echo Time 1: $(date)

mkdir /data/myrepo
cd /data/myrepo
git init
git switch -c main

cp -r /data/src-1/* .

git add .
git commit -m 'Initial commit'

export FAKETIME="2021-06-29 18:27:19"
echo Time 2: $(date)

cp -r /data/src-2/* .

git add .
git commit -m 'Add some content'

export FAKETIME="2022-03-18 19:02:11"
echo Time 3: $(date)

cp -r /data/src-3/* .

git add .
# "Accidentally" use personal email when on phone
git config --global user.email elin.andersson.96@penguinmail.com
git commit -m 'Add photos from my phone' -m 'Having a terminal app on my phone is so convenient!'

git config --global user.email voiceofnature@penguinmail.com

export FAKETIME="2025-01-21 18:29:34"
echo Time 4: $(date)

cp -r /data/src-4/* .

git add .
git commit -m 'Update blog' -m 'Will investigate GitHub'

git config --global user.email 196124613+VoiceOfNature@users.noreply.github.com

export FAKETIME="2025-01-22 13:13:19"
echo Time 5: $(date)

cp -r /data/src-5/* .

git add .
git commit -m 'Update blog' -m 'Talk about the exciting news that I am moving to GitHub Pages'

export FAKETIME="2025-02-22 16:03:27"
echo Time 6: $(date)

cp -r /data/src-6/* .

git add .
git commit -m 'Add photos'

export FAKETIME="2025-02-25 12:28:29"
echo Time 7: $(date)

cp -r /data/src-7/* .

git add .
git commit -m 'Finally moving to GitHub Pages!' -m 'Also refreshing the look as it was boring'

git log
