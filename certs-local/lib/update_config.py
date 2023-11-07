# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2023 Gene C
"""
 Update kernel config(s)
 Gene 2022-04-30
"""
import os
import uuid

from .utils import open_file

def _save_config(new_config_rows, conf_temp, conf, verb):
    """
    Write the udpated config
     - first update temp then rename
    """
    new_config = ''.join(new_config_rows)
    if verb:
        print (f'Updating config: {conf}')

    fobj = open_file(conf_temp, 'w')
    if fobj:
        fobj.write(new_config)
        fobj.close()
        os.rename(conf_temp, conf)
    else:
        print (f'Failed to write : {conf_temp}')
        return False
    return True

def _update_one_config(genkeys, kconfig_path, signing_key):
    """
    update a kernel config
    """
    #
    # always make temp in same dir to avoid rename across file systems
    #
    kconfig_dir = os.path.dirname(kconfig_path)
    kconfig_name_temp = str(uuid.uuid4())
    kconfig_path_temp = os.path.join(kconfig_dir, kconfig_name_temp)

    conf_name = 'CONFIG_SYSTEM_TRUSTED_KEYS='

    # read existing config
    fobj = open_file(kconfig_path, 'r')
    if fobj:
        kconfig_rows = fobj.readlines()
        fobj.close()
    else:
        print (f'Failed to open : {kconfig_path}')
        return False

    changed = True
    config_rows = []
    for row in kconfig_rows:
        if row.startswith(conf_name):
            rsplit = row.split('=')
            cur_signing_key = rsplit[1]
            if cur_signing_key == signing_key:
                changed = False
                break
            new_row = conf_name + signing_key
            config_rows.append(new_row)
        else:
            config_rows.append(row)

    if changed:
        if not _save_config(config_rows, kconfig_path_temp, kconfig_path, genkeys.verb):
            return False
    else :
        if genkeys.verb:
            print ('config up to date')

    return True

def update_configs(genkeys):
    """
    Update configs with new keys if needed
    Safest is to always read the current link and check config regardless if key was refreshed.
    """
    all_ok = True

    #
    # Confirm path to actual directory and not the link name which doesn't change
    #
    keydir = None
    keyname = 'signing_key.pem'
    keycur = os.path.join(genkeys.cert_dir, 'current')

    if os.path.islink(keycur) :
        keydir = os.readlink(keycur)
        keydir = os.path.join(genkeys.cert_dir, keydir)
        keydir = os.path.abspath(keydir)
        signing_key = os.path.join(keydir, keyname)

        if not os.path.exists(signing_key):
            print(f'Failed to find signing key: {signing_key}')
            return not all_ok
        #
        # format to match RHS of kernel config file
        #
        signing_key = '"' + signing_key + '"\n'
    else:
        print (f'Missing : {keycur}')
        return not all_ok

    for kconfig in genkeys.kconfig_list:
        kconfig_path = os.path.abspath(kconfig)
        okay = _update_one_config(genkeys, kconfig_path, signing_key)
        all_ok = all_ok | okay

    return all_ok
