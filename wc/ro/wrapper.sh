#!/bin/bash

cd /opt/ctf/wc/rw

if [[ "i386" == "i386" ]] || [[ "x86_64" == "i386" ]] ; then
  ../ro/wc 2>/dev/null
else
  qemu-i386 ../ro/wc 2>/dev/null
fi
