#!/bin/bash
#
# Installed in /etc/dkms/kernel-sign.sh
#
#  This is called via POST_BUILD for each module 
#  We use this to sign in the dkms build directory.  
#

cd ../$kernelver/$arch/module/

#SIGN=$kernel_source_dir/certs-local/sign_manual.sh
SIGN=/usr/lib/modules/$kernelver/build/certs-local/sign_manual.sh

if [ -f $SIGN ] ;then

   list=$(/bin/ls -1 *.ko 2>/dev/null)
   listxz=$(/bin/ls -1 *.ko.xz  2>/dev/null)
   listzstd=$(/bin/ls -1 *.ko.zst 2>/dev/null)

   if [ "$list" != "" ]  ; then
       for mod in $list
       do
           echo "DKMS: Signing kernel ($kernelver) module: $mod"
           $SIGN "$mod"
       done
   fi

   if [ "$listzstd" != "" ]  ; then
       for mod in $listzstd
       do
           echo "DKMS: Signing kernel ($kernelver) module: $mod"
           modunc=${mod%.zst}
           zstd -d $mod
           $SIGN "$modunc"
           echo "    : compress zstd ($kernelver) module: $modunc"
           zstd -f $modunc
           rm -f $modunc
       done
   fi

   if [ "$listxz" != "" ]  ; then
       for mod in $listxz
       do
           echo "DKMS: Signing kernel ($kernelver) module: $mod"
           modunc=${mod%.xz}
           xz -d $mod
           $SIGN "$modunc"
           echo "    : compress xz ($kernelver) module: $modunc"
           xz $modunc
           rm -f $modunc
       done
   fi

else
   echo "kernel $kernelver doesn't have out of tree module signing tools"
   echo "skipping signing out of tree modules"
fi


