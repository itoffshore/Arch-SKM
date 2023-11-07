#!/usr/bin/python
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2023 Gene C
"""
 Match kernel config signing key / hash
 Gene 2022-04-30
"""
from .utils import open_file

# ------------------------
# Local support functions
#
def config_to_key_type(config):
    """
    Identify key type
    """
    ktype = None
    csplit = config.split('=')
    name = csplit[0]
    if name.endswith('RSA'):
        ktype = 'rsa'
    elif name.endswith('ECDSA'):
        ktype = 'ec'
    else:
        print(f'Unknown kernel config {config}')
    return ktype

def config_to_hash_type(config):
    """
    Identify hash type
    """
    csplit = config.split('=')
    khash = csplit[1]
    khash = khash.strip().strip('"')
    return khash
# ------------------------

def get_key_hash_types(genkeys):
    """
    Read kernel config to determine:
     - module signing key type
     - module hash type
    """
    # pylint: disable=too-many-branches
    isokay = True

    #
    # forget why we added multiple config support - someone asked for it maybe?
    # config name came from reading dir, failing to open would be unlikely
    # If multiple configs, then check all using same key/hash types
    #
    num_errors = 0
    key_type = None
    hash_type = None

    for kconfig in genkeys.kconfig_list:
        fobj = open_file(kconfig, 'r')
        if fobj:
            conf_items = fobj.readlines()
            fobj.close()
        else:
            print (f'Failed to open : {kconfig}')
            num_errors += 1
            continue

        #
        # Find the hash and key type lines
        #
        num_to_find = 2
        count = 0
        for item in conf_items:
            if item.startswith('CONFIG_MODULE_SIG_KEY_TYPE_'):
                this_key_type = config_to_key_type(item)
                count += 1

                if not this_key_type:
                    print(f'Error in config {kconfig}')
                    num_errors += 1

                elif not key_type:
                    key_type = this_key_type

                elif this_key_type != key_type:
                    print(f'key_types must be same across configs: {key_type} vs {this_key_type}')
                    num_errors += 1


            elif item.startswith('CONFIG_MODULE_SIG_HASH'):
                this_hash_type = config_to_hash_type(item)
                count += 1

                if not this_hash_type:
                    print(f'Error in config {kconfig}')
                    num_errors += 1

                elif not hash_type:
                    hash_type = this_hash_type

                elif this_hash_type != hash_type:
                    print(f'config hash_types must be same : {hash_type} vs {this_hash_type}')
                    num_errors += 1

            if count >= num_to_find:
                break

        if count < num_to_find:
            print(f' Failed to find kernel sign key or hash type : {kconfig}')
            isokay = False

    if num_errors > 0:
        print(' Errors in kernel config file(s)')
        isokay = False

    if key_type:
        genkeys.ktype = key_type

    if hash_type:
        genkeys.khash = hash_type

    return isokay
