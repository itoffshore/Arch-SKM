#!/usr/bin/python
#
"""
# install_certs.py
#
# Called from package_headers()
#
# Installs the current keys and signing scripts.
#   .. certs-local/current -> dest_dir
#   .. certs-local/sign_module.py -> dest_dir
#   .. certs-local/signer_class.py -> dest_dir
#   .. certs-local/utils.py -> dest_dir
#
# Takes 1 Argument which is the destination directory
# Must reside in same certs-local directory with key/certs.
#
# To be used in PKGBUILD
#
# The destination directory will be created if it doesn't exist
#
"""
# Gene 2022-04-31
#
import os
import sys
import utils

#
# Extract self dir and dest dir
#
def _parse_args(av):

    err = None
    src_dir = None
    dst_dir = None
    # check dest dir
    if len(av) < 2:
        err = 'Missing destination dir'

    dst_dir = av[1]
    if os.path.exists(dst_dir) and not os.path.isdir(dst_dir):
        err = 'Bad destination - is not a dir : ' + dst_dir

    if err:
        print (err)
    else:
        os.makedirs(dst_dir, exist_ok=True)
        src_dir = os.path.dirname(av[0])
        src_dir = os.path.abspath(src_dir)

    return src_dir, dst_dir

def _run_prog_verb(pargs):

    ok = True
    [rc, _stdout, stderr] = utils.run_prog(pargs)
    if rc != 0:
        ok = False
        print ('Error  with : ' + ' ' .join(pargs))
        if stderr:
            print(stderr)

    return ok

def main():
    """
     install_certs
     Installs certificates and tools needed to sign module
    """

    src_dir,dst_dir = _parse_args(sys.argv)
    if not dst_dir:
        return

    cur_path = os.path.join(src_dir, 'current')
    key_dir = os.readlink(cur_path)
    key_dir = os.path.join(src_dir, key_dir)
    key_dir = os.path.abspath(key_dir)

    signer = os.path.join(src_dir, 'sign_module.py')
    signer_class = os.path.join(src_dir, 'signer_class.py')
    futils = os.path.join(src_dir, 'utils.py')

    # list of things to copy to dst_dir
    flist = [cur_path, key_dir, signer, signer_class, futils]
    pargs = ['/usr/bin/rsync', '-a'] + flist + [dst_dir]

    ok = _run_prog_verb(pargs)
    if not ok:
        return

    return


# ----------------------------
if __name__ == '__main__':
    main()
# ----------------------------
