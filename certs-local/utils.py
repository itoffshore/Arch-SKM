#!/usr/bin/python
#
# Support module for kernel signing tools
#
# Gene 2022-04-31
#
import os
import sys
import subprocess
import datetime
import glob

#------------------------------------------------------------------------
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

#------------------------------------------------------------------------
# Current date time
#
def date_time_now() :
    today = datetime.datetime.today()
    return today

#------------------------------------------------------------------------
# shell glob a file list
#
def file_list_glob(pathname) :

    flist = glob.glob(pathname, recursive=False)

    return flist
