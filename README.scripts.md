If `~/.config/abk.conf` exists the following **USER configurable variables** will be sourced by `abk`:
```
BUILD_DIR=~/build
GUI_EDITOR=mousepad
CONSOLE_EDITOR=nano
MAIN_KERNELS=linux linux-hardened linux-lts linux-zen
AUR_KERNELS=linux-hardened-cacule linux-xanmod-cacule linux-ck linux-amd
MAKEPKG_DIR=/tmp/makepkg
```
Edit to suit your `local` environment.

---

* Run `abk` with no parameters to view it's `help` information:
```
Usage: abk [OPTIONS]
	[ -u ] : update [ kernel-name ]
	[ -b ] : build [ kernel-name ]
	[ -i ] : install [ kernel-name / AUR pkgname ]
	[ -y ] : yes ( assume YES answers during build stage )
	[ -c ] : clean [ /path/to/directory ] ( quickly with rsync )
	[ -s ] : clean makepkg source dir selectively ( $SRCDEST )
	[ -l ] : clean makepkg log dir selectively ( $LOGDEST )
	[ -o ] : remove old packages selectively ( $PKGDEST )
	[ -w ] : print build log warnings [ kernel-name ]
	[ -h ] : this help message

Run the following 3 commands in sequence with a kernel variant to build a signed kernel:
----------------------------------------------------------------------------------------
 abk -u linux-hardened
 abk -b linux-hardened
 abk -i linux-hardened

The -i option can also print a menu with version choices for any manually built package e.g:
--------------------------------------------------------------------------------------------
 abk -i AUR-pkgname

The build stage can assume YES for running automated
----------------------------------------------------
 abk -y -b linux-hardened

Automated mode can also be enabled by adding AUTOMATED=Y to your ~/.config/abk.conf

Utilities:
-----------------------------------------------------
 abk -c /path/to/somewhere
 abk -s  (selectively clean makepkg $SRCDEST)
 abk -l  (selectively clean makepkg $LOGDEST)
 abk -o  (selectively clean makepkg $PKGDEST with paccache)
 abk -w kernel-name (selectively print build log warnings & errors)

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
---

**Automated Mode**
-----

**Update Stage** (added in `0.3.2`)

* The initial update stage will now try to apply a patchset to update a `PKGBUILD` instead of opening `GUI_EDITOR` / `CONSOLE_EDITOR` for manual editing.

*   Initially the following kernels are supported:
```
* linux-amd
* linux-ck
* linux-hardened
* linux-libre
* linux-lts
* linux
* linux-zen
```

* If a `patch` cannot be applied cleanly `abk` will fall back to manual operation with the configured `EDITORS` & generate a new `patch`.
* To test any newly generated patch simply re-run `abk -u kernel-variant`

---

**Build Stage** (added in `0.3.1`)

* `abk -y -b kernel-variant` will run the build step assuming `yes` answers to all questions
* Alternatively add `AUTOMATED=Y` to your `~/.config/abk.conf` & run `abk -b kernel-variant`
* Module compression is left unchanged
* Kernels will be automatically overwritten
* `makepkg` build directory will be automatically cleaned


---

**AUR Kernel Notes**
-----

* NB: some AUR kernel `PKGBUILD` do not use `$_srcname` & `$builddir` variables that the officially supported kernels do. For some AUR kernels you will need to set values to match the Package Maintainer's variable:
```
linux-xanmod-cacule:

prepare() {
  local _srcname=linux-${_major}

  # Out-of-tree module signing
```

* Other AUR kernels may also need `$builddir` set to match the Package Maintainer's variable for the module build directory inside the package:
```
_package-headers() {
  local builddir="$pkgdir/usr/lib/modules/$(<version)/build"
```
To make the example changes that open in `GUI_EDITOR` during kernel configuration work as noted below.

* Some AUR kernels may also need the **Kernel module signing facility** enabled if for example the following file does not exist in the package:
`/usr/lib/modules/kernel-variant/build/scripts/sign-file`

* For these unconfigured kernels you will see `sign-file.c` inside the package's modules build scripts directory.

* See also: [Kernel module signing facility](https://www.kernel.org/doc/html/v5.13/admin-guide/module-signing.html?highlight=module%20signing)
---

* With the [arch-sign-modules](https://aur.archlinux.org/packages/arch-sign-modules/) AUR package installed, during the first `update` stage the configured `GUI_EDITOR` will open the [PKGBUILD configuration example](https://github.com/itoffshore/Arch-SKM/blob/master/Arch-Linux-PKGBUILD-example) with instructions to edit the kernel `PKGBUILD` which will simultaneously open in the configured `CONSOLE_EDITOR`.

* :heavy_check_mark: Don't forget to add `module.sig_enforce=1` to `GRUB_CMDLINE_LINUX` in `/etc/default/grub` & `update-grub` if you have the AUR package [update-grub](https://aur.archlinux.org/packages/update-grub/) installed.
