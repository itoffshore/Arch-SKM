#!/usr/bin/python
#
# Create new pub/priv key pair for signing out of tree kernel modules.
#
# Each key pair is stored by date-time
# Python version of genkeys.sh with extra options
#
# This tool replaces both of the older bash scripts:  genkeys.sh and fix_config.sh
#
# NB: We always check the config - even if not refreshing keys to be sure it has the current signing key.
#
# Default refresh key is 7 days
# Gene 2022-04-30
#
import os
import sys
import stat
import subprocess
import datetime
import argparse
import uuid
import re

import pdb

#------------------------------------------------------------------------
#
# Runs external program (no shell)
#
def run_prog (pargs):

    ret = subprocess.run(pargs, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    rc = ret.returncode
    output = None
    errors = None
    if ret.stdout :
        output = str(ret.stdout, 'utf-8',errors='ignore')
    if ret.stderr :
        errors = str(ret.stderr, 'utf-8',errors='ignore')

    return [rc, output, errors]

#
# Command line options
#
def initialize() :
    me = os.path.basename(sys.argv[0])
    ap = argparse.ArgumentParser(description=me)

    verb = False
    refresh = '7d'
    kconfig = '../config'

    ap.add_argument('-r',  '--refresh', help='key refresh period (' + refresh + ') Example "7days",  "24h" or "always"')
    ap.add_argument('-c',  '--config',  help='Kernel Config file (' + kconfig + ') - updated with new key')
    ap.add_argument('-v',  '--verb', action='store_true', help='Verbose')

    parg = ap.parse_args()
    if parg.refresh:
        refresh = parg.refresh
    if parg.verb:
        verb = parg.verb
    if parg.config:
        kconfig = parg.config

    # read kernel config and check for EC in config
    khash,ktype = kern_config_hash(kconfig)
    conf = {
            'refresh' : refresh,
            'kconfig' : kconfig,
            'khash'   : khash,
            'ktype'   : ktype,
            'verb'    : verb,
           }

    return conf

#------------------------------------------------------------------------
#
# Check kernel config :
#   1) Get hash.
#   2) Confirm EC is in config
#
def kern_config_hash(kconfig):

    # default
    khash = 'sha512'
    ktype = 'rsa'

    match_conf = {'ec'   : 'CONFIG_MODULE_SIG_KEY_TYPE_ECDSA', 
                  'hash' : 'CONFIG_MODULE_SIG_HASH',
                 }

    fp = open(kconfig, 'r')
    if fp:
        count = 0
        conf_items = fp.readlines()
        for item in conf_items: 
            if item.startswith(match_conf['ec']) :
               ktype = 'ec'
               count = count + 1
            if item.startswith(match_conf['hash']) :
                khash = item.split('=')[1]
                khash = khash.strip('"\n')
            if count >= 2:
                break
    return khash,ktype

#------------------------------------------------------------------------
# 
# Update config with new keys if needed
# Safest is to always read the current link and check config regardless if key was refreshed.
# 
def update_config(conf):

    ok = True

    verb = conf['verb']
    kconfig_path = conf['kconfig']
    kconfig_dir = os.path.dirname(kconfig_path)
    kconfig_name = os.path.basename(kconfig_path)
    kdir = None
    kcur = 'current'
    keyname = 'signing_key.pem'
    kconfig_name_temp = str(uuid.uuid4())
    kconfig_path_temp = os.path.join(kconfig_dir, kconfig_name_temp)

    conf_name = 'CONFIG_SYSTEM_TRUSTED_KEYS='
    if os.path.islink(kcur) :
        kdir = os.readlink(kcur)
        if kdir:
            cwd = os.getcwd()
            signing_key = os.path.join(cwd, kdir, keyname)
            signing_key = os.path.normpath(signing_key)
            signing_key = '"' + signing_key + '"\n'

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
                        new_row = conf_name + signing_key + '\n'
                        new_rows.append(new_row)
                else:
                    new_rows.append(row)


            if changed:
                if verb:
                    print ('Updating config')
                fp = open(kconfig_path_temp, 'w')
                for row in new_rows:
                    fp.write(row)
                fp.close()
                os.rename(kconfig_path_temp, kconfig_path)
            else :
                if verb:
                    print ('config up to date')
    if not kdir:
        ok = False
        print ('Failed to find signing key')

    return ok

#------------------------------------------------------------------------
#
# Current date time
#
def date_time_now() :
    today = datetime.datetime.today()
    return today

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
    [rc, stdout, stderr] = run_prog(pargs)

    if rc != 0:
        print('Error making new key')
        if verb and stderr:
            print(stderr)
        return not ok
    os.chmod (kkey, stat.S_IREAD|stat.S_IWRITE)

    cmd = 'openssl pkey -in ' + kkey + ' -out ' +  kprv
    pargs = cmd.split()
    [rc, stdout, stderr] = run_prog(pargs)
    if rc != 0:
        print('Error making prv key')
        if verb and stderr:
            print(stderr)
        return not ok

    cmd = 'openssl x509 -outform der -in ' + kkey + ' -out '  + kcrt
    pargs = cmd.split()
    [rc, stdout, stderr] = run_prog(pargs)
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

    khash = conf['khash'] 
    ktype = conf['ktype'] 
    now = date_time_now()
    now_str = now.strftime('%Y%m%d-%H%M')

    kdir = os.path.join('./', now_str)
    os.makedirs(kdir, exist_ok=True)

    kvalid = '36500'
    kx509 = './x509.oot.genkey' 
    kbasename = 'signing'
    kprv = os.path.join(kdir, kbasename + '_prv.pem')
    kkey = os.path.join(kdir, kbasename + '_key.pem')
    kcrt = os.path.join(kdir, kbasename + '_crt.crt')

    ok = create_new_keys(conf, ktype, kvalid, kx509, khash, kprv, kkey, kcrt)
    if not ok:
        return

    # update current link to new kdir
    if ok:
        link_temp = str(uuid.uuid4())
        os.symlink(kdir, link_temp)
        os.rename(link_temp, 'current')

    return ok

#------------------------------------------------------------------------
# check_refresh()
#
# Is it time to create new keys
#
def check_refresh(conf):

    ok = True
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

        now = date_time_now()
        if next_dt > now:
            ok = False

    return ok

def main():

    #pdb.set_trace()
    conf = initialize()
    verb = conf['verb']

    key_refresh = check_refresh(conf)
    if key_refresh:
        if verb:
            print ('Refreshing keys')
        ok = make_new_keys (conf)
    elif verb:
        print ('Not time to refresh keys')

    ok = update_config(conf )

    return

# ----------------------------
if __name__ == '__main__':
    main()
# ----------------------------
