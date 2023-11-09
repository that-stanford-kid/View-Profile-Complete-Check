"""scrape"""
import urllib.request,urllib.error
from html.parser import HTMLParser
import sys, codecs
sys.stdout = codecs.getwriter('utf_16')(sys.stdout.buffer, 'strict')

print (__doc__)

search=input("Enter search words: ") or "python programming language"
search=search.replace(" ","_")
url="https://en.wikipedia.org/wiki/"+search
print("\nsearch word(s):",search)
resp=""

try:
    resp = urllib.request.urlopen(url)
except urllib.error.HTTPError:
    print("error occured")
    exit()
except:
    print("error occured")
    exit()

status=resp.getcode()
print("\nstatus code:",status)
html = str(resp.read())

class MyHTMLParser(HTMLParser): 
    def __init__(self):
        super().__init__()
        self.p=False
        self.pbuf=[]
    def handle_starttag(self, tag, attrs): 
        if(tag=="p"):
            self.p=True
            self.pbuf=[]
    def handle_endtag(self, tag): 
        if(tag=="p"):
            self.p=False
            print("".join(self.pbuf),flush=1)
    def handle_data(self, data): 
        if(self.p):
            data=data.replace("\\n","\n")
            data=data.replace("\\","")
            self.pbuf.append(data)


if(status==200):
    parser = MyHTMLParser()
    parser.feed(html)
