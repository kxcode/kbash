kbash
=====

Exploit GNU Bash Env Command Injection via Google.

CVE-2014-6271

Version 2.1

# usage

Batch Exploit GNU Bash Env Command Injection base on Google. Version 2.1 

optional arguments:
  -h, --help       show this help message and exit
  -u URL           specific a single Target Url
  -d DORK          Custom Google Dork,Using Google Search to find targets
  -t THREAD_COUNT  thread count
  -c PAGE_COUNT    crawl google page count
  -e CMD           Command to Execute
  -p PROXY         proxy,support:socks4,socks5,http eg:
                   socks5://127.0.0.1:1234

License, requests, etc: https://github.com/KxCode

kbash will print the status_code and url for each target responsed to exploitation.

#proxy
For socks proxy support. 
  1. Download Sockipy project from http://sourceforge.net/projects/socksipy/?source=directory.
  2. Copy the socks.py into the same directory as kbash.py


