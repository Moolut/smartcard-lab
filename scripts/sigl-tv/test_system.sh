#!/bin/bash

if [ "X$1" == "X" ]
then
  echo "Beschreibung:"
  echo "$0 video-file"
  echo ""
  echo "The video file will be encrypted by streamer.py, passed"
  echo "to receiver.py, which decrypts it with help of the smart"
  echo "card and playing back using mplayer."
  echo "Care: This will only work if the key in streamer.py"
  echo "and the one in the smart card match."
  exit 1
fi

cat $1 | python3 streamer.py | python3 receiver.py | mplayer -cache 300 -
