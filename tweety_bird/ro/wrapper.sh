#!/bin/bash

cd /opt/ctf/tweety_bird/rw

if [[ "i386" == "i386" ]] || [[ "x86_64" == "i386" ]] ; then
  ../ro/tweety_bird 2>/dev/null
else
  qemu-i386 ../ro/tweety_bird 2>/dev/null
fi