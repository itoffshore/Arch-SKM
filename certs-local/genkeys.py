#!/usr/bin/python
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

 (This tool replaces both of the older bash scripts:  genkeys.sh and fix_config.sh)
 NB:
   We always check the config - even if not refreshing keys to be sure it has the
   current signing key.

  Default refresh key is 7 days
"""
# Gene 2022-04-30
#
import os
import sys
import stat
import datetime
import argparse
import uuid
import re

#import pdb
import utils

def open_file(path, mode):
    """"
    Open a file and return file object
    """
    try:
        fobj = open(path, mode, encoding='utf-8')

    except OSError as err:
        print(f'Error opening file {path} : {err}')
        fobj = None

    return fobj


#------------------------------------------------------------------------
class GenKeys :
    """
    Class to help create and out of tree kernel signing keys
    """
    def __init__(self) :
        """
        Command line args and initialize
        """
        myname = os.path.basename(sys.argv[0])
        cert_dir = os.path.dirname(sys.argv[0])
        self.cert_dir = os.path.abspath(cert_dir)
        self.cwd = os.getcwd()

        if self.cwd == self.cert_dir:
            self.config = '../config'
        else:
            self.config = './config'

        self.verb = False
        self.refresh = '7d'
        self.khash = 'sha512'
        self.ktype = 'ec'
        self.kconfig_list = None
        self.okay = True

        par = argparse.ArgumentParser(description=myname)

        par.add_argument('-r',  '--refresh',
                default = self.refresh,
                help=f'key refresh period ({self.refresh}) E.g. "7d", "24h", "always"')

        par.add_argument('-c',  '--config',
                default = self.config,
                help=f'Kernel Config(s) to be updated ({self.config})'
                    + ' - wildcards ok (quote to avoid shell expansion).')

        par.add_argument('-kh', '--khash',
                default = self.khash,
                help=f'Hash type ({self.khash})')

        par.add_argument('-kt', '--ktype',
                default = self.ktype,
                help=f'Crypto algo ({self.ktype}) - Must be either ec or rsa')

        par.add_argument('-v',  '--verb',
                action='store_true', default = self.verb,
                help='Verbose ({self.verb})')

        parsed = par.parse_args()
        if parsed:
            for (opt,val) in vars(parsed).items() :
                setattr(self, opt, val)

        self.kconfig_list = utils.file_list_glob(self.config)
        if not self.kconfig_list :
            print ('No matching kernel config files found')
            self.okay = False

    def check_kern_config(self):
        """
        # Check kernel config(s) :
        # The config(s) checked to ensure hash and key_type match whats expected
        """
        okay = True

        setting = {
                'rsa' : 'CONFIG_MODULE_SIG_KEY_TYPE_RSA',
                'ec'  : 'CONFIG_MODULE_SIG_KEY_TYPE_ECDSA',
                }
        to_match = {
                'ktype' : setting[self.ktype],
                'khash' : 'CONFIG_MODULE_SIG_HASH',
                }
        want_get = {
                'ktype' : 'y',
                'khash' : self.khash,
                }


        # check each config warn if mismatch
        num_to_match = len(to_match)
        num_with_errors = 0
        for kconfig in self.kconfig_list:
            fobj = open_file(kconfig, 'r')
            if fobj:
                conf_items = fobj.readlines()
                fobj.close()
            else:
                print (f'Failed to open : {kconfig}')
                num_with_errors += 1
                continue

            count = 0
            for item in conf_items:
                for ckey,cval in to_match.items():
                    if item.startswith(cval):
                        count += + 1
                        want = want_get[ckey]
                        found = item.split('=')[1]
                        found = found.strip('"\n')
                        found = found.lower()
                        if found != want:
                            print (f'Bad {ckey} in {kconfig}  Want {want}, got {found}')
                            num_with_errors += 1

                    if count >= num_to_match:
                        # stop when get required config items
                        break

        if num_with_errors > 0:
            num_kconfigs = len(self.kconfig_list)
            print (f' {num_with_errors} out of {num_kconfigs} bad kernel config files')
            return not okay
        return okay

    def update_configs(self):
        """
        Update configs with new keys if needed
        Safest is to always read the current link and check config regardless if key was refreshed.
        """
        all_ok = True

        # ensure we get path to actuak directory and not the link name which doesn't change
        keydir = None
        keyname = 'signing_key.pem'
        keycur = os.path.join(self.cert_dir, 'current')

        if os.path.islink(keycur) :
            keydir = os.readlink(keycur)
            keydir = os.path.join(self.cert_dir, keydir)
            keydir = os.path.abspath(keydir)
            signing_key = os.path.join(keydir, keyname)
            #signing_key = os.path.normpath(signing_key)
            if not os.path.exists(signing_key):
                print(f'Failed to find signing key: {signing_key}')
                return not all_ok
            #
            # format to match RHS of kernel config file
            #
            signing_key = '"' + signing_key + '"\n'
        else:
            print ('Missing : {keycur}')
            return not all_ok

        for kconfig in self.kconfig_list:
            kconfig_path = os.path.abspath(kconfig)
            okay = self._update_one_config(kconfig_path, signing_key)
            all_ok = all_ok | okay

        return all_ok

    def _update_one_config(self, kconfig_path, signing_key):
        """
        update a single kernel config
        """
        okay = True
        kconfig_dir = os.path.dirname(kconfig_path)

        # always make temp in same dir to avoid rename across file systems
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

        changed = True
        new_rows = []
        for row in kconfig_rows:
            if row.startswith(conf_name):
                rsplit = row.split('=')
                cur_signing_key = rsplit[1]
                if cur_signing_key == signing_key:
                    changed = False
                    break
                new_row = conf_name + signing_key
                new_rows.append(new_row)
            else:
                new_rows.append(row)

        if changed:
            new_config = ''.join(new_rows)
            if self.verb:
                print ('Updating config: ' + kconfig_path)

            fobj = open_file(kconfig_path_temp, 'w')
            if fobj:
                #for row in new_rows:
                #    fobj.write(row)
                fobj.write(new_config)
                fobj.close()
                os.rename(kconfig_path_temp, kconfig_path)
            else:
                print (f'Failed to write : {kconfig_path_temp}')
        else :
            if self.verb:
                print ('config up to date')

        return okay

    def _create_new_keys(self, kvalid, kx509, kprv, kkey, kcrt):
        """
        Make the actual keys - rsa or ec using openssl
        """
        okay = True

        # new key
        cmd = f'openssl req -new -nodes -utf8 -{self.khash} -days {kvalid}'
        cmd = cmd + f' -batch -x509 -config {kx509}'
        cmd = cmd + f' -outform PEM -out {kkey} -keyout {kkey}'

        if self.ktype == 'ec':
            cmd = cmd + ' -newkey ec -pkeyopt ec_paramgen_curve:secp384r1'

        pargs = cmd.split()
        [retc, _stdout, stderr] = utils.run_prog(pargs)
        if retc != 0:
            print('Error making new key')
            if self.verb and stderr:
                print(stderr)
            return not okay

        os.chmod (kkey, stat.S_IREAD|stat.S_IWRITE)

        # extract private key
        cmd = f'openssl pkey -in {kkey} -out {kprv}'
        pargs = cmd.split()
        [retc, _stdout, stderr] = utils.run_prog(pargs)
        if retc != 0:
            print('Error making prv key')
            if self.verb and stderr:
                print(stderr)
            return not okay

        # Extract certificate (public) part
        cmd = f'openssl x509 -outform der -in {kkey} -out {kcrt}'
        pargs = cmd.split()
        [retc, _stdout, stderr] = utils.run_prog(pargs)
        if retc != 0:
            print('Error making crt')
            if self.verb and stderr:
                print(stderr)
            return not okay
        return okay

    def make_new_keys (self):
        """
        # Set up before we use openssl to create_new_keys()
        """
        okay = True
        if self.verb:
            print ('Making new keys ')

        now = utils.date_time_now()
        now_str = now.strftime('%Y%m%d-%H%M')

        kdir = os.path.join(self.cert_dir, now_str)
        os.makedirs(kdir, exist_ok=True)

        kvalid = '36500'
        kx509 =  os.path.join(self.cert_dir, 'x509.oot.genkey')
        kbasename = 'signing'
        kprv = os.path.join(kdir, kbasename + '_prv.pem')
        kkey = os.path.join(kdir, kbasename + '_key.pem')
        kcrt = os.path.join(kdir, kbasename + '_crt.crt')

        khash_file = os.path.join(kdir, 'khash')
        ktype_file = os.path.join(kdir, 'ktype')

        okay = self._create_new_keys(kvalid, kx509, kprv, kkey, kcrt)
        if not okay:
            return not okay

        #
        # Put khash and ktype files in key dir.
        # The module signing script will read the hash/ktype
        #
        fobj = open_file(khash_file,'w')
        if fobj:
            fobj.write(self.khash + '\n')
            fobj.close()
        else:
            print (f'Failed to write : {khash_file}')

        fobj = open_file(ktype_file,'w')
        if fobj:
            fobj.write(self.ktype + '\n')
            fobj.close()
        else:
            print (f'Failed to open : {ktype_file}')

        # update current link to new kdir
        # since the 'current' link and the actual keydir are in same dir we use
        # relative for link - safest in case certs-local is moved
        if okay:
            link_temp = str(uuid.uuid4())
            link_temp = os.path.join(self.cert_dir, link_temp)

            kdir_rel = os.path.basename(kdir)
            cur_link = os.path.join(self.cert_dir, 'current')

            os.symlink(kdir_rel, link_temp)
            os.rename(link_temp, cur_link)

        return okay

    def check_refresh(self):
        """
        # check if key refresh is needed
        """
        okay = True
        if not self.refresh:
            return okay
        if self.refresh.lower() == 'always':
            return okay

        # get the refresh time
        parse = re.findall(r'(\d+)(\w+)', self.refresh)[0]
        if parse and len(parse) > 1:
            freq = int(parse[0])
            units = parse[1]
        else:
            print ('Failed to parse refresh string')
            return okay

        kfile = os.path.join(self.cert_dir, 'current', 'signing_key.pem')
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
            now = utils.date_time_now()
            if next_dt > now:
                okay = False
        return okay

def main():
    """
    # genkeys - makes out-of-tree kernel module signing keys
    """
    #pdb.set_trace()
    genkeys = GenKeys()
    if not genkeys.okay:
        print ('Problem initializing')
        return 0

    if not genkeys.check_kern_config() :
        return 0

    if genkeys.check_refresh() :
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
