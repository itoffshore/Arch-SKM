Version [0.3.8]                                                       - 20220520
 - update graphical session detection in check_config()

Version [0.3.7]                                                       - 20220520
 - small bugfix for check_config() broken by changes for shellcheck tests

Version [0.3.6]                                                       - 20220519
 - small bugfix for -o option broken by changes for shellcheck tests

Version [0.3.5]                                                       - 20220519
 - adds Arch-SKM 2.3.6 (more code tidy up)

Version [0.3.4]                                                       - 20220505
 - adds Arch-SKM 2.3.2 (code reorganization / pylint improvements)
 - docs improved for arch-sign-modules

Version [0.3.3]                                                       - 20220505
 - minor doc update

Version [0.3.2]                                                       - 20220504
 - includes Gene's Arch-SKM 2.2.0 pure python release

 - experimental functionality to automate the initial update step

   adds patch_pkgbuild() & patch_generator() with patches for officially
   supported kernels + some others:

 * linux-amd.patch
 * linux-ck.patch
 * linux-hardened.patch
 * linux-libre.patch
 * linux-lts.patch
 * linux.patch
 * linux-zen.patch

 linux-hardened & linux-lts will always be regularly tested.

 If a patch cannot be cleanly applied an option is given to generate a new patchset.

Version [0.3.1]                                                       - 20220503
 - adds `-y` option to assume YES answers to run the build stage in an automated manner
   setting `AUTOMATED=Y` in `~/.config/abk.conf` has the same effect

 - check `$KBUILD_DIR` exists at the start of the build stage to catch input errors

 - reuse pacman message style & colours

Version [0.3]                                                       - 20220502
 - abk convenience function: print a menu / install previously built AUR packages

   e.g 'abk -i zoom'

 - Gene's new python scripts from his 1.2.0 release:

   https://github.com/gene-git/Arch-SKM

   * genkeys.py
   * install-certs.py

   * genkeys.py now automatically regenerates kernel signing keys every 7 days by default.

   NB: for file globbing to work with wildcards the path must be quoted:

   genkeys.py --config '../config*'

   * install-certs.py kindly makes the required PKGBUILD configuration simpler.

Version [0.2.62]                                                    - 20210906
 - Add print_warnings() to selectively print build log warnings & errors
 - Remove unused $pkgbuild from install_kernel() & add detection for non existent
   kernels
 - Add remove_old_pkgs() to selectively clean PKGDEST with paccache
 - Add pacman-contrib as optional depends to provide paccache

Version [0.2.61]                                                    - 20210906
 - Add archive_config() to create tar.xz archive of existing kernel configuration
   during update_kernel()

Version [0.2.60]                                                    - 20210830
 - Command line switches & help menu implemented with getops
 - Add functionality to build AUR kernels
 - Add functionality to change module compression algorithm
 - Add support for signing gz compressed kernel modules
 - Update PKGBUILD-example so fix_config.sh detects 64bit / 32bit / armv7h kernel config
 - Display menu of installable kernel variant versions during install stage
 - Enable build logging & print log file locations once complete
 - `~/.makepkg.conf` & `/etc/makepkg.conf` are both sourced for variables
 - Optional removal of makepkg build directory after a failed or successful build
 - Makepkg SRCDEST can be selectively cleaned with `abk -s` (useful if you
   build in ram / zram)
 - Makepkg LOGDEST can be selectively cleaned with `abk -l`
 - Any directory can be cleaned quickly with `abk -c /some/dir` using rsync to clean
   which is faster than `rm -rf`

Version [0.2.54]                                                    - 20210812
  - Add configurable USER VAR functionality
  - Speed up old kernel source removal with rsync

Version [0.2.1]                                                     - 20200523
  - Add Arch Linux helper script

Version [0.2.0]                                                     - 20191115
  - TIdy up Readme

Version [0.2.0]                                                     - 20191110
  - TIdy up Readme

Version [0.1.0]                                                     - 20191110
  - Initial version
