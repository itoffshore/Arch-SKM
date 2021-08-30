#!/bin/bash
#
# Installed in /etc/dkms/kernel-sign.sh
#
#  This is called via POST_BUILD for each module
#  We use this to sign in the dkms build directory.
#
# Gene 20191110
#

cd ../$kernelver/$arch/module/

#SIGN=$kernel_source_dir/certs-local/sign_manual.sh
SIGN=/usr/lib/modules/$kernelver/build/certs-local/sign_manual.sh

if [ -f $SIGN ] ;then

   list=$(/bin/ls -1 *.ko *.ko.xz *.ko.zst *.ko.gz 2>/dev/null)

   if [ "$list" != "" ]  ; then
       for mod in $list
       do
           echo "DKMS: Signing kernel ($kernelver) module: $mod"
           $SIGN "$mod"
       done
   fi
else
   echo "kernel $kernelver doesn't have out of tree module signing tools"
   echo "skipping signing out of tree modules"
fi

exit 0
