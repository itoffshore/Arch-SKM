Version [0.2.6]                                                    - 20210830
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
