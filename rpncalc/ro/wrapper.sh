#!/bin/bash

cd /opt/ctf/rpncalc/rw

if [[ "i386" == "i386" ]] || [[ "x86_64" == "i386" ]] ; then
  ../ro/rpncalc 2>/dev/null
else
  qemu-i386 ../ro/rpncalc 2>/dev/null
fi