#!/bin/bash
#
# Out of Tree Module Sign script:
#
# This will be installed in 
#
# /usr/lib/modules/<kernel-vers>/build/certs-local
#
#  Uses dirs :
#    Tmp   - working directory
#
# Requires: bash,  rsync, hexdump, zstd, xz
# 
# Ensures that signing is idempotent.
#

#
# Inputs
#
HASH=sha512
Modules="$@"

#
# Where 
#
MyRealpath=$(realpath $0)
MyDirName=$(dirname $MyRealpath)
BuildDir=${MyDirName%/*}

SIGN=${BuildDir}/scripts/sign-file

#
# Keys
#
KEY=${MyDirName}/current/signing_key.pem
CRT=${MyDirName}/current/signing_crt.crt


#
# Sign them 
#
echo "Module signing key : $KEY"


function is_signed () {
     f=$1
     has_sig='n'
     #hexdump -C $f |tail  |grep 'Module sign' > /dev/null
     hexdump --e '"%_p"' $f |tail  |grep 'Module sign' > /dev/null
     rc=$?
     if [ $rc = 0 ] ; then
         has_sig='y' 
     fi
     echo $has_sig
}

#
# Do it
#
for mod in $Modules
do

    moddir=$(dirname $mod) 

    if [ "$moddir" = "." ] ; then
        moddir="./"
    fi

    #
    # Create Tmp
    #
    if [ ! -d $moddir/Tmp ] ; then
        mkdir -p $moddir/Tmp
    fi

    rsync -a $mod $moddir/Tmp/
    mod_tmp=$moddir/Tmp/${mod}

    #
    # Decompress tmp file if needed
    #

    ext=${mod##*.}
    isxz='n'
    iszstd='n'

    if [ "$ext" = "xz" ] ; then
        echo "Decompressing :"
        isxz='y'
        xz -f --decompress $mod_tmp
        mod_tmp=${mod_tmp%*.xz}
    fi

    if [ "$ext" = "zstd" ] ; then
        echo "Decompressing :"
        iszstd='y'
        zstd -f --decompress $mod_tmp
        mod_tmp=${mod_tmp%*.zstd}
    fi

    #
    # remove any existing signature before signing
    #
    is_sig=$(is_signed $mod_tmp)
    if [ "$is_sig" = 'y' ] ; then
        echo "Removing old sig :"
        strip --strip-debug $mod_tmp
    fi

    echo "Signing $mod_tmp"
    $SIGN  sha512 $KEY $CRT $mod_tmp

    if [ "$isxz" = "y" ] ; then
        echo "Compressing:"
        xz -f $mod_tmp
        mod_tmp=${mod_tmp}.xz
    fi

    if [ "$iszstd" = "y" ] ; then
        echo "Compressing:"
        zstd -f $mod_tmp
        mod_tmp=${mod_tmp}.zstd
    fi


    #
    # backup current and install newly signed module
    # How to backup without older module being treated as a real module?
    # Maybe create /usr/lib/modules/<vers>/module-backup/xxx
    # real modules are in usr/lib/modules/<vers>/kernel/xxx
    # so could derive backup path by s/kernel/module-backup/
    # rsync -a $mod $moddir/Prev/${mod}
    # problem is this script could be run on modules outside standard kernel module tree
    # so for now no backups
    #
    mv $mod_tmp $mod

done

exit 




