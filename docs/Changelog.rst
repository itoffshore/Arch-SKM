Changelog
=========

[3.0.1] ----- 2023-11-05
 * fix readme.rst  
 * update Docs/Changelog.rst Docs/kernel-sign.pdf  

[3.0.0] ----- 2023-11-05
 * * key and hash types are now read from the kernel config file. Keeps everything consistent.  
 * * Code re-org with supporing modules now moved to lib/xxx.py  
 * * Confirm code works with hash type *sha3-512* introduced in kernel 6.7  
 * Requires openssl 3.2+ / kernel 6.7+  

[2.6.1] ----- 2023-10-04
 * update Docs/Changelog.rst  
 * Fix from Author: Expertcoderz <expertcoderzx@gmail.com>  
 * Merge: 38d25c5705 55f6e37101  
 * Merge pull request #8 from Expertcoderz/patch-1  
 * Fix -v argument help text f-string  
 * Fix -v argument help text f-string  
 * update Docs/Changelog.rst  

[2.6.0] ----- 2023-09-27
 * Reorganize documrnts under Docs.  
 * Migrate to restructured text  
 * Now easy to build html and pdf docs using sphinx  
 * update CHANGELOG.md  

[2.5.1] ----- 2023-03-31
 * update changelog  
 * small README wordsmithing  
 * update CHANGELOG.md  

[2.5.0] ----- 2023-03-30
 * Use Full path to openssl executable /usr/bin/openssl  
 * Rename Changelog to CHANGELOG following our current release tools. Update  

[2.4.0] ----- 2023-01-06
 * Add SPDX licensing lines  
 * Update kernel doc reference link  
 * Update kernel.org doc link to more recent kernel  

[2.3.9] ----- 2022-05-25
 * suppress a few silly pylint warnings  

[2.3.8] ----- 2022-05-21
 * Remove uneeded exception we just added. It is a subclass of OSError and so not needed.  

[2.3.7] ----- 2022-05-21
 * utils open_file catches (OSError,FileNotFoundError) exceoptions now  

[2.3.6] ----- 2022-05-18
 * update changelog  
 * Fix open_file to only apply encoding to text files (thanks  pylint)  

[2.3.5] ----- 2022-05-18
 * - More tidy up - try keep pylint noise down so dont miss things it finds  
 * delete old stuff  
 * comment tweak  

[2.3.4] ----- 2022-05-18
 * Update Changelog  
 * More code tidying in genkeys  
 * little more tidyup - no functional changes  
 * Add missing date to Changelog  

[2.3.3] ----- 2022-05-09
 * update Changelog  
 * Use OSError exception which has replaced IOError  
 * Catch OSError when file open fails  

[2.3.2] ----- 2022-05-08
 * Ack and Tested by by @itoffshore  
 * update Changelog  
 * trivial tidy  

[2.3.1] ----- 2022-05-08
 * more code tidying  
 * Update Changelog  
 * fix typo for refresh check  
 * tidy and improve exception handling  
 * tidy  
 * more cleaning  
 * more tidy  
 * more tidy ups  
 * some code tidying  
 * another typo!  
 * typo  
 * fix file to name to avoid module conflict  

[2.3.0] ----- 2022-05-08
 * - Code re-org to be more robust and easier to read.  
 * - Introduce KernelModSigner class and ModuleTool class to help organize  
 * - Functionality is unchanged.  

[2.2.1] ----- 2022-05-04
 * Update Changelog and README to reflect sign_module.py replacing sign_manual.sh  
 * Changelog - add date for 2.2.0  

[2.2.0] ----- 2022-05-04
 * update changelog  
 * archive sign_manual.sh  
 * turn off dev to ready for production  
 * Improve module signing scripts:  
 * - sign_module.py replaces sign_manual.sh  
 * - dkms/kernel_sign.sh updated accordingly  
 * - install-certs updated accordingly  
 * - adds dependency : python-zstandard for handling zst compressed modules  
 * README - small markdown tweaks  

[2.1.1] ----- 2022-05-03
 * update changelog  
 * typo  

[2.1.0] ----- 2022-05-03
 * update Changelog  
 * The key type and hash are now saved in files along side the keys. This allows the signing script to read them, and this means it no longer has hardcoded hash.  the sign script falls back on sha512 in case of previous key directory without a saved hash  
 * remove extraneous |  

[2.0.0] ----- 2022-05-02
 * update changelog  
 * word smith README  
 * fix markdown on last addition  

[1.3.5] ----- 2022-05-02
 * Update README and Changelog  
 * Add few more words about some available tooks by @itoffshore  

[1.3.4] ----- 2022-05-02
 * Update Changelog  
 * White space patches from @itoffshore  

[1.3.3] ----- 2022-05-02
 * Update Changelog  
 * Typo in echo found by @itoffshore  
 * Changelog udpate  
 * Add reference to @itoffshore aur package and github repo  

[1.3.2] ----- 2022-05-02
 * Fix hexdump typo "--e" to "-e"  
 * Changelog update  
 * Mindor markdown tweaks  

[1.3.1] ----- 2022-05-02
 * typo fix  
 * Update Changelog  

[1.3.0] ----- 2022-05-02
 * Per @ittoffshore, add comment about quoting wildcard characters  
 * Fixes from @itoffshore  
 * 1. For manual signing  
 * zstd modules use .zst instead of .zsrd  
 * support for gzip  
 * 2. For dkms  
 * Add gzip support  

[1.2.0] ----- 2022-05-01
 * Expand help with reminder wildcards must be quoted  

[1.1.0] ----- 2022-05-01
 * tweak the prepare() example  
 * small word smithing  

[1.0.1] ----- 2022-05-01
 * remove debugging  

[1.0.0] ----- 2022-05-01
 * Update readme and changelog  
 * genkeys now handles multiple configs using shell glob with --config  
 * support utilities  
 * Rename tools to utils  
 * Share coupld functions via tools.py  
 * Add install-certs.py for use by package_headers() to simplify PKGBUILD  
 * Update package_headers() to remove reference to file no longer being created. Part of issue #3  
 * Add a little markdown to Changlelog.md  
 * Update changes for 0.8.0 and 0.8.1  

[0.8.1] ----- 2022-04-30
 * Remove references to now unused scripts  

[0.8.0] ----- 2022-04-30
 * fix typo  
 * Tidy up README  
 * As per itoffshore check for key exists prior to getting mtime. Fixes bug in check_refresh()  

[0.7.0] ----- 2022-04-30
 * version [0.7.0]                                                     - 20220430  
 * - Add genkeys.py (replaces both genkeys.sh and fix_config.sh)  
 * This supports refresh key frequency (default is 7 days)  
 * PKGBUILD use: ./genkeys.py -v  
 * Creates new keys as needed and updates kernel config.  
 * version [0.6.0]                                                     - 20220430  
 * - Support zstd module compression in sign_manual.sh  
 * - Improve hexdump for signed module detection in sign_manual.sh  
 * - Has hardcoded sha512 hash - needs updating/replacing  
 * version [0.5.0]                                                     - 20220420  
 * - Switch to using elliptic curve  

[0.4.0] ----- 2021-10-20
 * Update kernel-sign.sh for compressed modules  

[0.3.0] ----- 2019-11-15
 * Tidy Readme  

[0.2.0] ----- 2019-11-10
 * tidy up readme  

[0.1.0] ----- 2019-11-10
 * Initial revision  

