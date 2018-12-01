#!/bin/bash

cd /opt/ctf/no-rsa/rw

if [[ "i386" == "x86_64" ]] || [[ "x86_64" == "x86_64" ]] ; then
  ../ro/no-rsa 2>/dev/null
else
  qemu-x86_64 ../ro/no-rsa 2>/dev/null
fi