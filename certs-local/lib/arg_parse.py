# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2023 Gene C
"""
 Command line options
"""
import os
import sys
import argparse

from .utils import file_list_glob

def arg_parse(genkeys:'GenKeys') -> dict:
    """
    Parse command line and update genekeys
     - type hint is quoted to avoid circular include
    """
    # pylint: disable=line-too-long
    desc = os.path.basename(sys.argv[0])
    opts = []

    #
    # Available options
    #
    opt = [('-r',  '--refresh'), {'default' : genkeys.refresh,
            'help' : f'refresh period ({genkeys.refresh}) E.g. 7d, 24h, always'}]
    opts.append(opt)

    opt = [('-c',  '--config'), {'default' : genkeys.config,
            'help' : f'Kernel Config(s) ({genkeys.config}) - wildcards ok (quote to avoid shell expansion)'}]
    opts.append(opt)

    opt = [('-v',  '--verb'), {'action' : 'store_true', 'help' : 'Verbose (False)'}]
    opts.append(opt)

    #
    # deprecated options - keep and warn to avoid any script breakage
    #
    opt = [('-kh',  '--khash'), {'help' : 'khash deprecated - now read from kernel config'}]
    opts.append(opt)

    opt = [('-kt',  '--ktype'), {'help' : 'ktype deprecated - now read from kernel config'}]
    opts.append(opt)

    #
    # Add options and Parse
    #
    par = argparse.ArgumentParser(description=desc)
    for opt in opts:
        ((opt_s, opt_l), kwargs) = opt
        par.add_argument(opt_s, opt_l, **kwargs)
    #
    # save into genkeys
    #
    parsed = par.parse_args()
    if parsed:
        for (opt,val) in vars(parsed).items() :
            setattr(genkeys, opt, val)

    genkeys.kconfig_list = file_list_glob(genkeys.config)
    if not genkeys.kconfig_list :
        print ('No matching kernel config files found')
        genkeys.okay = False
