#!/bin/bash

cd /opt/ctf/KaaS/rw

if [[ "i386" == "x86_64" ]] || [[ "x86_64" == "x86_64" ]] ; then
  ../ro/KaaS 2>/dev/null
else
  qemu-x86_64 ../ro/KaaS 2>/dev/null
fi