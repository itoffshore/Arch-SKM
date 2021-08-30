#!/bin/bash
#
# Arg: config file
#
# Update kernel config : CONFIG_SYSTEM_TRUSTED_KEYS to use current keys
#
# Gene 20191110
#

Config="$1"


KeyDir=$(<current_key_dir)

sed -e "s|^CONFIG_SYSTEM_TRUSTED_KEYS=.*$|CONFIG_SYSTEM_TRUSTED_KEYS=\"../../certs-local/$KeyDir/signing_key.pem\"|"  < $Config  > $Config.tmp

mv $Config.tmp $Config

exit 0
