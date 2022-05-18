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
    retc = ret.returncode
    output = None
    errors = None
    if ret.stdout :
        output = str(ret.stdout, 'utf-8',errors='ignore')
    if ret.stderr :
        errors = str(ret.stderr, 'utf-8',errors='ignore')

    return [retc, output, errors]

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
    okay = True
    if os.path.exists(fpath):
        try:
            os.unlink(fpath)
            return okay
        except OSError as err:
            print(f'Failed to remove file : {fpath} Error : {err}')
            return not okay
    return okay

def open_file(path, mode):
    """
    open a file handlilng any exceptions
    Returns file object
    """
    try:
        fobj = open(path, mode, encoding='utf-8')

    except OSError as err:
        print(f'Error opening {path} : {err}')
        fobj = None

    return fobj
