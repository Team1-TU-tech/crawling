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
            rst = crawler(url_path)

            soup = BeautifulSoup(rst, 'html.parser')

            dl = soup.find_all("dl", "th_info")
            dd = soup.find_all("dd", "list_cont")

            if dl:
                soup_rst = str(dl[0]) + str(dd[0])
                soup_rst = re.sub('src="//image','src="http://image',soup_rst)
                print(":::::::::::: sh start :::::::::::::")
                with open(f"./crawl_{url_path}.html","w") as f:
                    f.write(str(soup_rst))
                #print(f"echo '{soup_rst}' >> crawl_{url_path}.html")
                #os.system(f"echo '{soup_rst}' >> crawl_{url_path}.html")
                print(":::::::::::: sh end :::::::::::::")
                with open(f"./crawl_{url_path}.html","a") as f:
                    f.write(str(transform(soup)))
                #os.system(f"echo \"{transform(soup)}\" >> crawl_{url_path}.html")
            print(f":::::::::::::::::::::::::::::::::::: {url_path} crawling end n 10 sleep :::::::::::::::::::::::::::::::::::::::::")
            sleep(10)
        set_offset(idx)
    else:
        raise Exception("IndexNotDefined")


def transform(html):
    soup = html

    if soup.find("dd", id="noticeTitle"):
        title = f'{soup.find("dd", id="noticeTitle").contents[-1].strip()}'.replace("\u200b"," ")
    else:
        title = f'{soup.find("dd", class_="title").contents[-1].strip()}'.replace("\u200b"," ")

    rst_dict = {
        "link": soup.find("a", class_=re.compile("btn_reserve")).get("href") if soup.find("a", class_=re.compile("btn_reserve")) else None,
        "title" : f"{title}" ,
        "openDate" : soup.find("dd", id="ticketOpenDatetime").contents[-1].strip(),
        "imgUrl" : re.sub("//image","http://image",soup.find("img", src=re.compile("//image*")).get("src")) if soup.find("img", src=re.compile("//image*")) else None
    }
    if list(filter( lambda x:"공연" in x.contents[-1], soup.find_all("p"))):
        for p in list(filter( lambda x:"공연" in x.contents[-1], soup.find_all("p"))):
            # if "공연 기간" in p.contents[-1].strip():
            #     rst_dict["showDate"]=p.contents[-1].strip().replace("공연 기간 :\xa0","")
            if re.findall("공연[\s]?기간", p.contents[-1].strip()) or re.findall("공연[\s]?일시", p.contents[-1].strip()):
                rst_dict["showDate"]=p.contents[-1].split(":")[-1].strip()
            elif re.findall("공연[\s]?시간", p.contents[-1].strip()):
                rst_dict["showTime"]=p.contents[-1].split(":")[-1].strip()
            elif re.findall("공연[\s]?장소", p.contents[-1].strip()):
                rst_dict["showLoca"]=p.contents[-1].split(":")[-1].strip()
            # elif "공연 시간" in p.contents[-1].strip():
            #     rst_dict["showTime"]=p.contents[-1].strip().replace("공연 시간 :\xa0","")
            # elif "공연 장소" in p.contents[-1].strip():
            #     rst_dict["showLoca"]=p.contents[-1].strip().replace("공연 장소 :\xa0","")
    #### p tag 와 div tag를 혼재하는 페이지가 있음.....
    # for i in soup.find_all("div"):
    #     print("div :::::::::::::", i, "공연" in i.contents[-1] if i.contents else None)
    if list(filter( lambda x:"공연" in x.contents[-1] if x.contents else None, soup.find_all("div"))):
        for div in list(filter( lambda x:"공연" in x.contents[-1] if x.contents else None, soup.find_all("div"))):

            # if "공연 기간" in div.contents[-1].strip():
            #     rst_dict["showDate"]=div.contents[-1].strip().replace("공연 기간 :\xa0","")
            # elif "공연 시간" in div.contents[-1].strip():
            #     rst_dict["showTime"]=div.contents[-1].strip().replace("공연 시간 :\xa0","")
            # elif "공연 장소" in div.contents[-1].strip():
            #     rst_dict["showLoca"]=div.contents[-1].strip().replace("공연 장소 :\xa0","")
            if re.findall("공연[\s]?기간", div.contents[-1].strip()) or re.findall("공연[\s]?일시", div.contents[-1].strip()):
                rst_dict["showDate"]=div.contents[-1].split(":")[-1].strip()
            elif re.findall("공연[\s]?시간", div.contents[-1].strip()):
                rst_dict["showTime"]=div.contents[-1].split(":")[-1].strip()
            elif re.findall("공연[\s]?장소", div.contents[-1].strip()):
                rst_dict["showLoca"]=div.contents[-1].split(":")[-1].strip()
    print(rst_dict)
    return rst_dict


def runtest(idx):
    idx=idx
    #oldest=43058
    oldest=get_offset()

    # html = crawler()
    # soup = BeautifulSoup(html, 'html.parser')
    #
    # ####### idx (최신 게시글번호) 설정 ##################
    # for a in soup.find_all("a"):
    #     if re.findall("notice/[0-9]+", a.get("href")):
    #         idx = int(a.get("href").split("/")[-1])
    #         break

    ####### idx ~ 가장 마지막 게시글까지 crawling ##################
    if idx>0:
        for url_path in range(idx,oldest-1,-1):
            print(f":::::::::::::::::::::::::::::::::::: {url_path} crawling start :::::::::::::::::::::::::::::::::::::::::")
            rst = crawler(url_path)

            soup = BeautifulSoup(rst, 'html.parser')

            dl = soup.find_all("dl", "th_info")
            dd = soup.find_all("dd", "list_cont")

            if dl:
                soup_rst = str(dl[0]) + str(dd[0])
                soup_rst = re.sub('src="//image','src="http://image',soup_rst)
                print(":::::::::::: sh start :::::::::::::")
                with open(f"./crawl_{url_path}.html","w") as f:
                    f.write(str(soup_rst))
                #print(f"echo '{soup_rst}' >> crawl_{url_path}.html")
                #os.system(f"echo '{soup_rst}' >> crawl_{url_path}.html")
                print(":::::::::::: sh end :::::::::::::")
                with open(f"./crawl_{url_path}.html","a") as f:
                    f.write(str(transform(soup)))
                #os.system(f"echo \"{transform(soup)}\" >> crawl_{url_path}.html")
            print(f":::::::::::::::::::::::::::::::::::: {url_path} crawling end n 10 sleep :::::::::::::::::::::::::::::::::::::::::")
            sleep(10)
        set_offset(idx)
    else:
        raise Exception("IndexNotDefined")