# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2023 Gene C
"""
 Check if time to make new keys
"""
import os
import datetime
import re

from .utils import date_time_now
from .utils import open_file

def _read_current_khash(genkeys):
    """
    Read existing khash
    """
    khash = None
    khash_path = os.path.join(genkeys.cert_dir, 'current', 'khash')
    fob = open_file(khash_path, 'r')
    if fob:
        khash = fob.read()
        fob.close()
        khash = khash.strip()
    return khash

def refresh_needed(genkeys):
    """
    check if key refresh is needed
     - if older than refresh time
     - if hash type has changed - need to refresh to be consistent
     Returns:
        True if need refresh
    """

    #
    # no refresh time or always refresh
    #
    if not genkeys.refresh:
        return True
    if genkeys.refresh.lower() == 'always':
        return True

    #
    # kernel hash type mismatch to current hash
    # i.e. check genkeys.khash vs current/khash
    #
    khash_current = _read_current_khash(genkeys)
    if not khash_current or khash_current != genkeys.khash:
        print('Current hash doesnt match kernel config - updating')
        return True
    #
    # Has clock expired - get the refresh time
    #
    parse = re.findall(r'(\d+)(\w+)', genkeys.refresh)[0]
    if parse and len(parse) > 1:
        freq = int(parse[0])
        units = parse[1]
    else:
        print ('Failed to parse refresh string')
        return True

    kfile = os.path.join(genkeys.cert_dir, 'current', 'signing_key.pem')
    if os.path.exists(kfile) :
        mod_time = os.path.getmtime(kfile)
        curr_dt = datetime.datetime.fromtimestamp(mod_time)

        match units[0]:
            case 's':
                timedelta_opts = {'seconds' : freq}
            case 'm':
                timedelta_opts = {'minutes' : freq}
            case 'h':
                timedelta_opts = {'hours' : freq}
            case 'd':
                timedelta_opts = {'days' : freq}
            case 'w':
                timedelta_opts = {'weeks' : freq}

        next_dt = curr_dt + datetime.timedelta(**timedelta_opts)
        now = date_time_now()
        if next_dt > now:
            return False
    return True
