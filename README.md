kbash
=====

Exploit GNU Bash Env Command Injection via Google.

CVE-2014-6271

#desc

Exploit GNU Bash Env Command Injection via Google. 


optional arguments:


-  -h, --help       show this help message and exit
-  -t THREAD_COUNT  thread count
-  -c PAGE_COUNT    google page count
-  -e CMD           Command to Execute

kbash will print the status_code and url for each target responsed to exploit.

#proxy
For socks proxy support. 
  1. Download Sockipy project from http://sourceforge.net/projects/socksipy/?source=directory.
  2. Copy the socks.py into the same directory as kbash.py
  3. if you dont need proxy, you can delete the three lines near the comment "PROXY"


