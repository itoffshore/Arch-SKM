If `~/.config/abk.conf` exists USER configurable variables will be sourced by `abk`:
```
BUILD_DIR=~/build
GUI_EDITOR=mousepad
CONSOLE_EDITOR=nano
```

edit to suit your local environment.

Run `abk` with no parameters to view it's `help` information:

```
[~/git/Arch-SKM/scripts]$ ./abk

ERROR: missing valid command from: 'update build install' as 1st parameter
ERROR: missing kernel variant: 'linux-xxxx' as 2nd parameter

Available kernels:

linux
linux-hardened
linux-lts
linux-zen

To build a kernel run commands 'update build install' in sequence with a kernel variant:

Example command: ./abk update linux-hardened
Example command: ./abk build linux-hardened
Example command: ./abk install linux-hardened
```
