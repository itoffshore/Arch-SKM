#!/usr/bin/python
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2023 Gene C
"""
 Create new pub/priv key pair for signing out of tree kernel modules.
 This program must reside in the certs-local dir but can be run from any directory.
 It will use it's own path to locate the cert-local dir

 Each key pair is stored by date-time

 Args:
  refresh  - time before new keys are created. e.g. --refresh 24h
             default is 7days. Units may be abbreviateed and one of secs, mins, hours,
             days or weeks
  khash    - sets hash (default is sha512)
  ktype    - rsa or ec (default is ec)
  config   - config file to update with signing key. May contain wildcard
             e.g. --config config
                  --config ../configs/config.*

 NB:
   We always check the config - even if not refreshing keys to be sure it has the
   current signing key.

  Default refresh key is 7 days
Gene 2022-04-30
"""

#import pdb
from lib import GenKeys

def main():
    """
    # genkeys - makes out-of-tree kernel module signing keys
    """
    #pdb.set_trace()
    genkeys = GenKeys()
    if not genkeys.okay:
        print ('Problem initializing')
        return 0

    if genkeys.refresh_needed() :
        genkeys.make_new_keys()

    elif genkeys.verb:
        print ('Key refresh not needed yet')

    # always update to be sure config has key even if no refresh
    genkeys.update_configs()

    return 0

# ----------------------------
if __name__ == '__main__':
    main()
# ----------------------------
