If `~/.config/abk.conf` exists the following **USER configurable variables** will be sourced by `abk`:
```
BUILD_DIR=~/build
GUI_EDITOR=mousepad
CONSOLE_EDITOR=nano
MAIN_KERNELS=linux linux-hardened linux-lts linux-zen
AUR_KERNELS=linux-hardened-cacule linux-xanmod-cacule linux-ck linux-zen-lts510
MAKEPKG_DIR=/tmp/makepkg
```
Edit to suit your `local` environment.

---

* Run `abk` with no parameters to view it's `help` information:
```
Usage: abk [OPTIONS]
	[ -u ] : update [ kernel-name ]
	[ -b ] : build [ kernel-name ]
	[ -i ] : install [ kernel-name ]
	[ -c ] : clean [ /path/to/directory ] ( quickly with rsync )
	[ -s ] : clean makepkg source dir selectively ($SRCDEST)
	[ -l ] : clean makepkg log dir selectively ($LOGDEST)
	[ -h ] : this help message

Run the following 3 commands in sequence with a kernel variant to build a signed kernel:
----------------------------------------------------------------------------------------
 abk -u linux-hardened
 abk -b linux-hardened
 abk -i linux-hardened

Utilities:
----------
 abk -c /path/to/somewhere
 abk -s  (selectively clean makepkg source directory)
 abk -l  (selectively clean makepkg log directory)

Configured kernels:
-------------------
* linux
* linux-lts
* linux-hardened
* linux-zen
* linux-hardened-cacule
* linux-xanmod-cacule
* linux-ck
* linux-libre
```
* NB: some AUR kernel `PKDBUILD` do not use `$_srcname` & `$builddir` variables that the officially supported kernels do. For some AUR kernels you will need to set values to match the Package Maintainer's variable:
```
linux-xanmod-cacule:

prepare() {
  _srcname=linux-${_major}

  # Out-of-tree module signing
```

Other AUR kernels may also need `$builddir` set to match the Package Maintainer's variable for the module build directory inside the package:
```
_package-headers() {
  local builddir="$pkgdir/usr/lib/modules/$(<version)/build"
```
To make the example changes that open in `GUI_EDITOR` during kernel configuration work as noted below.

Some AUR kernels may also need the Kernel module signing facility enabled if for example the following file does not exist in the package:
`/usr/lib/modules/kernel-variant/build/scripts/sign-file`

For these unconfigured kernels you will see `sign-file.c` inside the package's modules build scripts directory.

See also: [Kernel module signing facility][(https://www.kernel.org/doc/html/v5.13/admin-guide/module-signing.html?highlight=module%20signing)
--- 

* With the [arch-sign-modules](https://aur.archlinux.org/packages/arch-sign-modules/) AUR package installed, during the first `update` stage the configured `GUI_EDITOR` will open the [PKGBUILD configuration example](https://github.com/itoffshore/Arch-SKM/blob/master/Arch-Linux-PKGBUILD-example) with instructions to edit the kernel `PKGBUILD` which will simultaneously open in the configured `CONSOLE_EDITOR`.

* :heavy_check_mark: Don't forget to add `module.sig_enforce=1` to `GRUB_CMDLINE_LINUX` in `/etc/default/grub` & `update-grub` if you have the AUR package [update-grub](https://aur.archlinux.org/packages/update-grub/) installed.
