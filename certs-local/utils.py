#!/usr/bin/python
"""
# Support module for kernel signing tools
"""
# Gene 2022-04-31
#
import os
import subprocess
import datetime
import glob

#------------------------------------------------------------------------
# Runs external program (no shell)
#
def run_prog (pargs):
    """
     Runs executable program with arguments.
     Returns status along with stdout and stderr
    """
    ret = subprocess.run(pargs, stdout = subprocess.PIPE, stderr = subprocess.PIPE, check=False)
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
    """
     Return current datetime
    """
    today = datetime.datetime.today()
    return today

#------------------------------------------------------------------------
# shell glob a file list
#
def file_list_glob(pathname) :
    """
     Return list of files match glob path
    """
    flist = glob.glob(pathname, recursive=False)
    return flist

# ------------------------------------------------------
# unlink/remove file (not directory)
#
def remove_file(fpath):
    """
     Remove a file (not a dir.
    """
    ok = True
    if os.path.exists(fpath):
        try:
            os.unlink(fpath)
            return ok
        except  Exception as err:
            print('Failed to remove file : ' + fpath + ' Error : ' + str(err))
            return not ok
    return ok
