from bs4 import BeautifulSoup
from time import sleep
import re
import os

from crawling.utils import get_offset, set_offset
from crawling.crawler import crawler


def run():
    idx=-1
    #oldest=43058
    oldest=get_offset()

    html = crawler()
    soup = BeautifulSoup(html, 'html.parser')

    ####### idx (최신 게시글번호) 설정 ##################
    for a in soup.find_all("a"):
        if re.findall("notice/[0-9]+", a.get("href")):
            idx = int(a.get("href").split("/")[-1])
            break

    ####### idx ~ 가장 마지막 게시글까지 crawling ##################
    if idx>0:
        for url_path in range(idx,oldest-1,-1):
            print(f":::::::::::::::::::::::::::::::::::: {url_path} crawling start :::::::::::::::::::::::::::::::::::::::::")
            rst=crawler(url_path)

            soup = BeautifulSoup(rst, 'html.parser')

            dl = soup.find_all("dl", "th_info")
            dd = soup.find_all("dd", "list_cont")

            if dl:
                soup_rst = str(dl[0]) + str(dd[0])
                soup_rst=re.sub('src="//image','src="http://image',soup_rst)
                os.system(f"echo '{soup_rst}' >> crawl_{url_path}.html")
            print(f":::::::::::::::::::::::::::::::::::: {url_path} crawling end n 10 sleep :::::::::::::::::::::::::::::::::::::::::")
            sleep(10)
        set_offset(idx)
    else:
        raise Exception("IndexNotDefined")
