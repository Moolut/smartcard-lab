#!/bin/bash

if [ "X$1" == "X" -o "X$2" == "X" ]
then
  echo "Beschreibung:"
  echo "$0 server port"
  echo ""
  echo "A connection to the server with the given port will be"
  echo "established and decrypted by receiver.py, which utilizes"
  echo "the connected smart card before playing back the video"
  echo "stream with mplayer or vlc."
  exit 1
fi

# nc $1 $2 | python3 receiver.py | mplayer -cache 500 - 2>/dev/null

nc $1 $2 | python3 receiver.py | vlc - vlc://quit
