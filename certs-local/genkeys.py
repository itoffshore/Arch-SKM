#!/usr/bin/python
#
# Create new pub/priv key pair for signing out of tree kernel modules.
# This program must reside in the certs-local dir but can be run from any directory.
# It will use it's own path to locate the cert-local dir
#
# Each key pair is stored by date-time
#
# Args:
#  refresh  - time before new keys are created. e.g. --refresh 24h
#             default is 7days. Units may be abbreviateed and one of secs, mins, hours, days or weeks
#  khash    - sets hash (default is sha512)
#  ktype    - rsa or ec (default is ec)
#  config   - config file to update with signing key. May contain wildcard
#             e.g. --config config
#                  --config ../configs/config.*
#
# (This tool replaces both of the older bash scripts:  genkeys.sh and fix_config.sh)
# NB:
#   We always check the config - even if not refreshing keys to be sure it has the current signing key.
#
# Default refresh key is 7 days
# Gene 2022-04-30
#
import os
import sys
import stat
import datetime
import argparse
import uuid
import re

import utils
import pdb

#
# Command line options
#
def initialize() :
    me = os.path.basename(sys.argv[0])
    cert_dir = os.path.dirname(sys.argv[0])
    cert_dir = os.path.abspath(cert_dir)
    cwd = os.getcwd()

    ap = argparse.ArgumentParser(description=me)

    verb = False
    refresh = '7d'
    if cwd == cert_dir:
        kconfig = '../config'
    else:
        kconfig = './config'
    khash = 'sha512'
    ktype = 'ec'

    ap.add_argument('-r',  '--refresh', help='key refresh period (' + refresh + ') E.g. "7d", "24h", "always"')
    ap.add_argument('-c',  '--config',  help='Kernel Config(s) to be updated (' + kconfig + ') - wildcards ok (please quote to avoid shell expansion).')
    ap.add_argument('-kh', '--khash',   help='Hash type (' + khash + ')')
    ap.add_argument('-kt', '--ktype',   help='Crypto algo (' + khash + ') - Must be either ec or rsa')
    ap.add_argument('-v',  '--verb', action='store_true', help='Verbose')

    parg = ap.parse_args()
    if parg.refresh:
        refresh = parg.refresh
    if parg.config:
        kconfig = parg.config
    if parg.khash:
        khash = parg.khash
    if parg.ktype:
        ktype = parg.ktype
    if parg.verb:
        verb = parg.verb

    kconfig_list = utils.file_list_glob(kconfig)
    if not kconfig_list or kconfig_list == []:
        print ('No matching kernel config files found')
        return None

    # read kernel config and check for EC in config
    #khash,ktype = kern_config_hash(kconfig)
    conf = {
            'cert_dir'  : cert_dir,
            'cwd'       : cwd,
            'refresh'   : refresh,
            'kconfig'   : kconfig,
            'kconfig_list' : kconfig_list,
            'khash'     : khash,
            'ktype'     : ktype,
            'verb'      : verb,
           }

    return conf

#------------------------------------------------------------------------
#
# Check kernel config(s) :
# The config(s) checked to ensure hash and key_type match whats expected
#
#   1) Get hash.
#   2) Confirm EC is in config
#
def check_kern_config(conf):

    ok = True
    khash = conf['khash']
    ktype = conf['ktype']
    kconfig_list = conf['kconfig_list']

    config = {
            'rsa' : 'CONFIG_MODULE_SIG_KEY_TYPE_RSA',
            'ec'  : 'CONFIG_MODULE_SIG_KEY_TYPE_ECDSA',
            }

    this_config_type = config[ktype]
    to_match = {'ktype' : this_config_type,
                'khash'  : 'CONFIG_MODULE_SIG_HASH',
               }
    want_get = {'ktype' : 'y',
                'khash' : khash,
               }

    num_to_match = len(to_match)

    # check each config warn if mismatch
    num_kconfigs = len(kconfig_list)
    num_with_errors = 0
    for kconfig in kconfig_list:
        fp = open(kconfig, 'r')
        if fp:
            conf_items = fp.readlines()
            fp.close ()
            count = 0
            for item in conf_items:
                for ckey, config_opt in to_match.items():
                    if item.startswith(config_opt):
                        count += + 1
                        want = want_get[ckey]
                        found = item.split('=')[1]
                        found = found.strip('"\n')
                        found = found.lower()
                        if found != want:
                            print ('Bad ' + ckey + ' in ' + kconfig + ' Want ' + want + ' found ' + found)
                            num_with_errors += 1

                if count >= num_to_match:
                    # quit if got the config items we need to check
                    break
        else:
            print ('Failed to open config : ' + kconfig)
            num_with_errors += 1

    if num_with_errors > 0:
        print (' ' + str(num_with_errors) + ' out of ' + str(num_kconfigs) + ' bad kernel config files')
        return not ok

    return ok

#------------------------------------------------------------------------
#
# Update config with new keys if needed
# Safest is to always read the current link and check config regardless if key was refreshed.
#
def update_configs(conf):

    all_ok = True
    verb = conf['verb']
    cert_dir = conf['cert_dir']
    kconfig_list = conf['kconfig_list']

    # ensure we get path to actuak directory and not the link name which doesn't change
    keydir = None
    curname = 'current'
    keyname = 'signing_key.pem'
    keycur = os.path.join(cert_dir, curname)

    if os.path.islink(keycur) :
        keydir = os.readlink(keycur)
        keydir = os.path.join(cert_dir, keydir)
        keydir = os.path.abspath(keydir)
        signing_key = os.path.join(keydir, keyname)
        #signing_key = os.path.normpath(signing_key)
        if not os.path.exists(signing_key):
            print('Failed to find signing key: ' + signing_key)
            return not all_ok
        #
        # format to match RHS of kernel config file
        #
        signing_key = '"' + signing_key + '"\n'
    else:
        print ('Missing : ' + keycur)
        return not all_ok

    for kconfig in kconfig_list:
        kconfig_path = os.path.abspath(kconfig)
        ok = update_one_config(conf, kconfig_path, signing_key)
        all_ok = all_ok | ok

    return all_ok

def update_one_config(conf, kconfig_path, signing_key):

    ok = True

    verb = conf['verb']

    kconfig_dir = os.path.dirname(kconfig_path)
    kconfig_name = os.path.basename(kconfig_path)

    # always make temp in same dir to avoid rename across file systems
    kconfig_name_temp = str(uuid.uuid4())
    kconfig_path_temp = os.path.join(kconfig_dir, kconfig_name_temp)

    conf_name = 'CONFIG_SYSTEM_TRUSTED_KEYS='

    # read existing config
    fp = open(kconfig_path, 'r')
    kconfig_rows = fp.readlines()
    fp.close()

    changed = True
    new_rows = []
    for row in kconfig_rows:
        if row.startswith(conf_name):
            rsplit = row.split('=')
            cur_signing_key = rsplit[1]
            if cur_signing_key == signing_key:
                changed = False
                break
            else:
                new_row = conf_name + signing_key
                new_rows.append(new_row)
        else:
            new_rows.append(row)

    if changed:
        if verb:
            print ('Updating config: ' + kconfig_path)
        fp = open(kconfig_path_temp, 'w')
        for row in new_rows:
            fp.write(row)
        fp.close()
        os.rename(kconfig_path_temp, kconfig_path)
    else :
        if verb:
            print ('config up to date')

    return ok

#------------------------------------------------------------------------
#
# Make the actual keys - rsa or ec using openssl
#
def create_new_keys(conf, ktype, kvalid, kx509, khash, kprv, kkey, kcrt) :

    verb = conf['verb']
    ok = True
    cmd = 'openssl req -new -nodes -utf8 -' + khash + ' -days ' + kvalid + ' -batch -x509 -config ' + kx509
    cmd = cmd + ' -outform PEM' + ' -out ' + kkey + ' -keyout ' + kkey
    if ktype == 'ec':
        cmd = cmd + ' -newkey ec -pkeyopt ec_paramgen_curve:secp384r1'

    pargs = cmd.split()
    [rc, stdout, stderr] = utils.run_prog(pargs)

    if rc != 0:
        print('Error making new key')
        if verb and stderr:
            print(stderr)
        return not ok
    os.chmod (kkey, stat.S_IREAD|stat.S_IWRITE)

    cmd = 'openssl pkey -in ' + kkey + ' -out ' +  kprv
    pargs = cmd.split()
    [rc, stdout, stderr] = utils.run_prog(pargs)
    if rc != 0:
        print('Error making prv key')
        if verb and stderr:
            print(stderr)
        return not ok

    cmd = 'openssl x509 -outform der -in ' + kkey + ' -out '  + kcrt
    pargs = cmd.split()
    [rc, stdout, stderr] = utils.run_prog(pargs)
    if rc != 0:
        print('Error making crt')
        if verb and stderr:
            print(stderr)
        return not ok

    return ok

#------------------------------------------------------------------------
#
# Set up before we use openssl to create_new_keys()
#
def make_new_keys (conf):

    ok = True
    cert_dir = conf['cert_dir']
    verb = conf['verb']

    if verb:
        print ('Making new keys ')

    khash = conf['khash']
    ktype = conf['ktype']
    now = utils.date_time_now()
    now_str = now.strftime('%Y%m%d-%H%M')

    kdir = os.path.join(cert_dir, now_str)
    os.makedirs(kdir, exist_ok=True)

    kvalid = '36500'
    kx509 =  os.path.join(cert_dir, 'x509.oot.genkey')
    kbasename = 'signing'
    kprv = os.path.join(kdir, kbasename + '_prv.pem')
    kkey = os.path.join(kdir, kbasename + '_key.pem')
    kcrt = os.path.join(kdir, kbasename + '_crt.crt')

    khash_file = os.path.join(kdir, 'khash')
    ktype_file = os.path.join(kdir, 'ktype')

    ok = create_new_keys(conf, ktype, kvalid, kx509, khash, kprv, kkey, kcrt)
    if not ok:
        return

    #
    # khash and ktype in same dir - the signing script will read the hash to use
    #
    fp = open(khash_file,'w')
    if fp:
        fp.write(khash + '\n')
        fp.close()
    else:
        print ('Failed to open (w) : ' + khash_file)

    fp = open(ktype_file,'w')
    if fp:
        fp.write(ktype + '\n')
        fp.close()
    else:
        print ('Failed to open (w) : ' + ktype_file)

    # update current link to new kdir
    # since the 'current' link and the actual keydir are in same dir we use
    # relative for link - safest in case certs-local is moved
    if ok:
        link_temp = str(uuid.uuid4())
        link_temp = os.path.join(cert_dir, link_temp)

        kdir_rel = os.path.basename(kdir)
        cur_link = os.path.join(cert_dir, 'current')

        os.symlink(kdir_rel, link_temp)
        os.rename(link_temp, cur_link)

    return ok

#------------------------------------------------------------------------
# check_refresh()
#
# Is it time to create new keys
#
def check_refresh(conf):

    ok = True
    verb = conf['verb']
    refresh = conf.get('refresh')

    if not refresh:
        return ok
    if refresh.lower() == 'always':
        return ok

    # get the refresh time
    parse = re.findall('(\d+)(\w+)', refresh)[0]
    if parse:
        freq = parse[0]
        freq = int(freq)
        if len(parse) > 1:
            units = parse[1]
        else:
            print ('Refresh error = missing units')
            return ok
    else:
        print ('Failed to parse refresh string')
        return ok

    kfile = os.path.join('current', 'signing_key.pem')
    if os.path.exists(kfile) :
        mod_time = os.path.getmtime(kfile)
        curr_dt = datetime.datetime.fromtimestamp(mod_time)

        if units.startswith('s'):
            next_dt = curr_dt + datetime.timedelta(seconds=freq)
        elif units.startswith('m'):
            next_dt = curr_dt + datetime.timedelta(minutes=freq)
        elif units.startswith('h'):
            next_dt = curr_dt + datetime.timedelta(hours=freq)
        elif units.startswith('d'):
            next_dt = curr_dt + datetime.timedelta(days=freq)
        elif units.startswith('w'):
            next_dt = curr_dt + datetime.timedelta(weeks=freq)

        now = utils.date_time_now()
        if next_dt > now:
            ok = False

    return ok

def main():

    #pdb.set_trace()
    conf = initialize()
    if not conf:
        return

    verb = conf['verb']
    if not check_kern_config(conf) :
        return

    if check_refresh(conf) :
        ok = make_new_keys (conf)
    elif verb:
        print ('Key refresh not needed yet')

    ok = update_configs(conf)

    return

# ----------------------------
if __name__ == '__main__':
    main()
# ----------------------------
