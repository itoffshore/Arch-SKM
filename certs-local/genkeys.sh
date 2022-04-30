#!/bin/bash
#
# Create new pub/priv key pair for signing out of tree kernel modules.
#
# Each key pair is stored by date-time
#

Dt=$(date +'%Y%m%d-%H%M')

mkdir -p $Dt
KernKey="${Dt}/signing_key.pem"
PrivKey="${Dt}/signing_prv.key"
KernCrt="${Dt}/signing_crt.crt"


#
# kernel config must have :
# CONFIG_MODULE_SIG_KEY_TYPE_ECDSA=y
# CONFIG_MODULE_SIG_HASH="sha512"        
#  script greps hash type from ../config but you can also hard code to be consistent
#
#hash="sha512"           
hash=$(grep CONFIG_MODULE_SIG_HASH ../config | sed -e 's/CONFIG_MODULE_SIG_HASH="//' -e 's/"//g')

#
# EC keys
#
openssl req -new -nodes -utf8 -${hash} -days 36500  -batch -x509 -config ./x509.oot.genkey \
    -outform PEM -out $KernKey -keyout $KernKey  -newkey ec -pkeyopt ec_paramgen_curve:secp384r1


chmod 0600 $KernKey
openssl pkey -in $KernKey -out $PrivKey
openssl x509 -outform der -in $KernKey -out $KernCrt

rm -f current; ln -s $Dt current

rm -f current_key_dir
echo "$Dt" > ./current_key_dir

exit 0
