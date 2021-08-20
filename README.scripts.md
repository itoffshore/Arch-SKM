If `~/.config/abk.conf` exists **USER configurable variables** will be sourced by `abk`:
```
BUILD_DIR=~/build
GUI_EDITOR=mousepad
CONSOLE_EDITOR=nano
```

Edit to suit your `local` environment.

---

* Run `abk` with no parameters to view it's `help` information:

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
* With the [arch-sign-modules](https://aur.archlinux.org/packages/arch-sign-modules/) AUR package installed, during the first `update` stage the configured `GUI_EDITOR` will open the [PKGBUILD configuration example](https://github.com/itoffshore/Arch-SKM/blob/master/Arch-Linux-PKGBUILD-example) with instructions to edit the kernel `PKGBUILD` which will simultaneously open in the configured `CONSOLE_EDITOR`.

* :heavy_check_mark: Don't forget to add `module.sig_enforce=1` to `GRUB_CMDLINE_LINUX` in `/etc/default/grub` & `update-grub` if you have the AUR package [update-grub](https://aur.archlinux.org/packages/update-grub/) installed.
