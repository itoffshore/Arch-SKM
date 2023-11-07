# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2023 Gene C
"""
 Main class for genkeys
 Gene 2022-04-30
"""
import os
import sys

from .arg_parse import arg_parse
from .get_key_hash import get_key_hash_types
from .update_config import update_configs
from .make_keys import make_new_keys
from .refresh_needed import refresh_needed

class GenKeys :
    """
    Class to create out of tree kernel signing keys
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self) :
        """
        Command line args and initialize
        """
        self.cert_dir = os.path.dirname(sys.argv[0])
        self.cert_dir = os.path.abspath(self.cert_dir)
        self.cwd = os.getcwd()

        if self.cwd == self.cert_dir:
            self.config = '../config'
        else:
            self.config = './config'

        self.verb = False
        self.refresh = '7d'
        self.khash = 'sha512'
        self.ktype = 'ec'
        self.kconfig_list = []
        self.okay = True

        #
        # parse command line options
        #
        arg_parse(self)

        #
        # Retrieve kernel module signing key and hash types
        #
        self.okay = get_key_hash_types(self)

    def update_configs(self):
        """
        Update configs with new keys if needed
        """
        if not update_configs(self):
            self.okay = False
        return self.okay

    def make_new_keys (self):
        """
        Set up before we use openssl to create_new_keys()
        """
        # pylint: disable=R0914
        if self.verb:
            print ('Making new keys ')

        if not make_new_keys(self):
            self.okay = False
        return self.okay

    def refresh_needed(self):
        """
        # check if key refresh is needed
        """
        return refresh_needed(self)
