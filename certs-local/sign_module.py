#!/usr/bin/python
# 
# ---------------
# sign_module.py
# ---------------
#
# Signs one or more kernel modules
#
# 2 use cases based on command line:
#   1) list of modules to sign
#       mod1 mod2 mod3 .. 
#
#   2) directory which has list of modules
#      -d <directory>
#
#  dkms uses (2) 
#
#  Modules can be uncompressed (.ko) or compressed with zstd (.zst), xz (.xz) or gzip (.gz)
#  Modules may also be already signed in which case the signature is stripped out before re-signing.
#  
# Replaces sign_manual.sh and new companion script dkms/kernel_sign.sh
#
# All functions are implemented within this file.
# (though we may split into separate files at later date)
#
#  NB - stripping removes all debug info including signature.
#
# Gene - 2022-0504
#
import os
import sys
import subprocess

import zstandard
import lzma
import gzip
import uuid

import pdb

# ------------------------------------------------------
# run external program (no shell)
# 
def run_prog (pargs):
    ret = subprocess.run(pargs, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    rc = ret.returncode
    output = None
    errors = None
    if ret.stdout :
        put = str(ret.stdout, 'utf-8',errors='ignore')
    if ret.stderr :
        errors = str(ret.stderr, 'utf-8',errors='ignore')
    return [rc, output, errors]

# ------------------------------------------------------
# unlink/remove file (not directory)
#
def remove_file(fpath):
    if os.path.exists(fpath):
        try:
            os.unlink(fpath)
        except:
            print('Failed to remove file : ' + fpath)
    return

# ------------------------------------------------------
# get_kernel_signer()
#
# This script is installed in each kernel build directory under certs-local.
# So, this uses that to locate the kernel build dir and hence the kernel compiled signing tool
#
# i.e.
#   me = '/usr/lib/modules/<kern-vers>/build/certs-local/sign_module.py'
#   signer = /usr/lib/modules/<kern-vers>/build/scripts/sign-file
#
def get_kernel_signer(me):
    signer = None
    my_path = os.path.realpath(me)
    my_dir = os.path.dirname(my_path)
    build_dir = os.path.dirname(my_dir)
    signer = os.path.join(build_dir, 'scripts/sign-file')

    return signer

# ------------------------------------------------------
# strip a file to remove sig
#
def strip_sig(mpath):

    ok = True
    pargs = ['/usr/bin/strip', '--strip-debug', mpath]
    [rc, output, errors] = run_prog(pargs)

    return rc

# ------------------------------------------------------
# Get key info
# /usr/lib/modules/<kern-vers>/build/certs-local/current/<info>
#
def get_key_info(me):

    my_path = os.path.realpath(me)
    my_dir = os.path.dirname(my_path)
    key = os.path.join(my_dir, 'current/signing_key.pem')
    crt = os.path.join(my_dir, 'current/signing_crt.crt')
    khash_file = os.path.join(my_dir, 'current/khash')
    khash = None
    if os.path.exists(khash_file) :
        fp = open(khash_file, 'r')
        if fp:
            khash = fp.read()
            khash = khash.strip()
            fp.close()
        else:
            khash = None
    else:
        khash = 'sha512'

    ok = True
    if not os.path.exists(key) :
        ok = False
        print ('Missing key file : ' + key)
    if not os.path.exists(crt) :
        ok = False
        print ('Missing crt file : ' + crt)

    key_info = {
            'ok'    : ok,
            'key'   : key,
            'crt'   : crt,
            'khash' : khash,
            }

    return key_info

# ------------------------------------------------------
# Does actual module signing Using key_info 
#
def sign_module(key_info, signer, mpath):

    khash = key_info['khash']
    key = key_info['key']
    crt = key_info['crt']

    pargs = [signer, khash, key, crt, mpath] 
    [rc, sout, serr] = run_prog(pargs)

    if rc != 0:
        print ('Signing failed')

    return rc


# ------------------------------------------------------
# check if module is signed 
#
def is_module_signed(data):
    signed = False
    sign_flag = b'Module signature'

    # 
    # minimize the search by looking in last few bytes = x
    #                 <- x -> 
    #   [0]------[N-x]-------[N-1]
    # 
    #  => N-x > x
    #
    chunk = 100
    size = len(data)
    b0 = 0
    b1 = size-1
    if size - chunk >= chunk:
        b0 = size - chunk 

    found = data.find(sign_flag, b0, b1) 
    if found >= 0:
        signed = True

    return signed

# ------------------------------------------------------
# 1, Compress signed temp module (if needed) 
# 2. rename temp module to original
#
def compress_rename_module(ptmp, mod) :
    ok = True
    (fpath,fext) = os.path.splitext(mod)

    if fext != '.ko' :
        #
        # compress
        #
        mod_data = None
        fp = open(ptmp, 'rb')
        if fp:
            raw_data = fp.read()
            fp.close()
        else:
            print('Failed to read uncompressed temp file : ' + ptmp)

        if fext == '.zst' :
            cctx = zstandard.ZstdCompressor()
            mod_data = cctx.compress(raw_data)

        elif fext == '.xz' :
            mod_data = lzma.compress(raw_data)

        elif fext == '.gz' :
            mod_data = gzip.compress(raw_data)

        else:
            print ('unkown extension - compress failed: ' + fext)
            return not ok

        fp = open(ptmp, 'wb')
        if fp:
            fp.write(mod_data)
            fp.close()
        else:
            print ('Failed to write compressed temp file: ' + ptmp)
            return not ok

    os.rename (ptmp, mod)

    return ok

# ------------------------------------------------------
# Read module into memory - decompress if needed
#
def read_module (mod):

    (fpath,fext) = os.path.splitext(mod)

    #
    # read module
    #
    mod_data = None
    if not os.path.exists(mod) or not  os.path.isfile(mod):
        print ('Module is not a file: ' + mod) 
        return None

    fp = open(mod, 'rb')
    if fp:
        raw_data = fp.read()
        fp.close()
    else:
        print('Failed to read : ' + mod)
        return None

    # decompress if needed
    if fext == '.ko':
        mod_data = raw_data

    elif fext == '.zst' :
        dctx = zstandard.ZstdDecompressor()
        mod_data = dctx.decompress(raw_data)

    elif fext == '.xz' :
        mod_data = lzma.decompress(raw_data)

    elif fext == '.gz' :
        mod_data = gzip.decompress(raw_data)

    else:
        print ('unkown extension : ' + fext)

    return mod_data

# ------------------------------------------------------
# process_one_module()
#
# Preps the module for actual signing - handle compressed and uncompressed and previously signed or not.
#
# As previously done, we use file extension to determine if/how compressed. We do not use magic bytes
#
# We work in memory rather than via filesystem - each module is small emough its not a problem
#
# While it may be fine to leave existing sig and sign the (previously) signed module - we choose to 
# strip it. Maybe simpler and cleaner not to bother - not clear if this may cause problem for
# kernel sig check or not. So we strip it out. This also removes any debug symbols so it has a different
# downside if the module had any.
#

def process_one_module (key_info, signer, modin):
    ok = True
    #
    # This reads and decompresses as needed
    #
    mod = os.path.abspath(modin)
    mod_data = read_module(mod)
    if not mod_data:
        return not ok

    #
    # save module as temp file ready to sign
    #
    has_sig = is_module_signed(mod_data)
    mod_dir = os.path.dirname(mod)
    ftmp = str(uuid.uuid4())
    ptmp = os.path.join(mod_dir, ftmp) 
    fp = open(ptmp, 'wb')
    if fp:
        fp.write(mod_data)
        fp.close()
    else:
        print('Failed to create temp mod file')
        return not ok

    if has_sig:
        ret = strip_sig(ptmp)

    #
    # Sign and re-compress
    #
    ret = sign_module(key_info, signer, ptmp)
    if ret != 0:
        print ('Failed to sign : ' + mod)
        remove_file(ptmp)
        return not ok
    ret = compress_rename_module(ptmp, mod)
    if not ret :
        remove_file(ptmp)
        return not ok

    return ok

# ------------------------------------------------------
# modules_from_dir()
# Returns list of (recognizable) modules located in a directory
#
def modules_from_dir(mdir):
    mod_list = None
    #
    # Uncompressed or compressed
    #
    known_exts = ['.ko', '.ko.zst', '.ko.xz', '.ko.gz']

    if not os.path.exists(mdir):
        print ('Module directory bad : ' + mdir)
        return None

    if not os.path.isdir(mdir):
        print ('Module directory must be a directory: ' + mdir)
        return None
    
    mod_dir = os.path.abspath(mdir)
    #
    # include files ending in one of known exts above -
    #
    mod_list = []
    scan = os.scandir(mod_dir)
    for item in scan:
        if item.is_file():
            for ext in known_exts:
                if item.name.endswith(ext):
                    mod_path = os.path.join(mod_dir, item.name)
                    mod_list.append(mod_path)
                    break

    return mod_list

# ------------------------------------------------------
# Usual command line handling.
#  1. modules listed
#  2. -d <module dir>
#
def main():
    # test / debug 
    #fake_me = '/usr/lib/modules/5.18.0-rc5-1-custom-00014-gef8e4d3c2ab1/build/certs-local/sign_manual.sh'
    #pdb.set_trace()

    #
    # directory or list of modules
    #
    av = sys.argv
    if len(av) == 1:
        print ('No modules to sign')

    me = av[0]
    if av[1] == '-d' :
        if len(av) >= 3:
            mod_dir = av[2]
        else:
            print ('Missing module dir after -d')
            return
        modules = modules_from_dir(mod_dir)
    else:
        modules = av[1:]

    if not modules :
        printing ('No modules to sign')
        return

    #
    # Sign all modules
    #
    signer = get_kernel_signer(me)      # fake me for testing outside kernel tree
    key_info = get_key_info(me)
    if not key_info['ok']:
        return

    for mod in modules:
        if os.path.exists(mod) :
            ret = process_one_module (key_info, signer, mod)
        else:
            print ('Module not found : ' + mod)

    return

# ----------------------------
if __name__ == '__main__':
    main()
# ----------------------------

