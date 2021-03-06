#####
# File Name: ptt_beauty_crawler.py
# Author: alen6516
# Created Time: 2018-02-06
#####
import re, sys, os, errno
import requests
requests.packages.urllib3.disable_warnings()
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import threading

DEBUG = 1

def msg(text):
    if DEBUG == 1:
        print(str(text))


class Beauty_crawler():
    def __init__(self):
        self.download_path='./'
        

    def set_path(self):
        self.download_path=input("give the path: (press Enter to cancel)\n")
        if not self.download_path:
            self.download_path='./'

        if self.download_path[-1]!='/':
            self.download_path+='/'
        if self.download_path[0]=='~':
            self.download_path=os.path.expanduser("~")+self.download_path[1:]

    def get_path(self):
        return self.download_path    

    def _get_title(self, soup):
        result = soup.find('meta', property="og:title")["content"]
        if ":" in result:
            result = "_".join(result.split(":"))
        return result

    def _get_post_time(self,soup):
        time_list=soup.find_all('span', {'class':'article-meta-value'})[-1].get_text().split(' ')
        # ['Wed', 'Feb', '', '7', '11:29:30', '2018']
        # ['Thu', 'Sep', '15', '22:57:26', '2016']
        year=time_list[-1]
        month=time_list[1]
        date=time_list[2] if time_list[2] else time_list[3]       
        return '('+year+"_"+month+"_"+date+')'
 
    def makedir(self, dir_name):
        try:
            os.makedirs(dir_name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def _write(self, filename, url):
        # to avoid errors occuring in ssl verification
        # using requests.get() to replace urlretrieve()
        with open(filename, 'wb') as f:
            resp=requests.get(url, verify=False)
            f.write(resp.content)

    def download(self, target):
        res=requests.get(target, verify=False)
        soup = BeautifulSoup(res.text, "html.parser")

        title = self._get_title(soup)
        post_time=self._get_post_time(soup)
        path=self.download_path+title+post_time+'/'
        self.makedir(path)

        for a in soup.find_all('a', href=True):
            res = re.search("href=\".+?\"", str(a)).group()
            url = res.split("\"")[1]
            
            if url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".gif"):
                msg(url)
                file_path=path+url.split('/')[-1]
                self._write(file_path, url)

if __name__=='__main__':
    crawler=Beauty_crawler()

    thread_list=[]

    op="1"

    try:
        while op!="0":
            op=input("[0]exit, [1] download, [2] set path, [3] show curr path:\n>>> ")
            if op=="0":
                for t in thread_list:
                    if t.is_alive():
                        print("wait for downloading before close")
                break
            
            elif op=="1":
                target_=input("give the target url:\n")
                t = threading.Thread(target=crawler.download, args=(target_,))
                t.start()
                thread_list.append(t)
                for t in thread_list:
                    if not t.is_alive():
                        thread_list.remove(t) 

            elif op=="2":
                crawler.set_path()

            elif op=="3":
                print("current download_path:\n%s" % crawler.get_path())
            
            else:
                print("wrong op, try again")
    except KeyboardInterrupt:
        for t in thread_list:
            if t.is_alive():
                print("wait for downloading before exit")

