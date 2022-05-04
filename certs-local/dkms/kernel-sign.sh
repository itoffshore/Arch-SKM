#!/bin/bash
#
# Installed in /etc/dkms/kernel-sign.sh
#
#  This is called via POST_BUILD for each module
#  We use this to sign in the dkms build directory.
#

SIGN=/usr/lib/modules/$kernelver/build/certs-local/sign_module.py

if [ -f $SIGN ] ;then
    $SIGN -d ../$kernelver/$arch/module/
else
   echo "kernel $kernelver doesn't have out of tree module signing tools"
   echo "skipping signing out of tree modules"
fi

exit
