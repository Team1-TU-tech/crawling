from crawling.crawler import crawling_data
import requests
from bs4 import BeautifulSoup

def scrap_data():
    get_link = crawling_data()

    print(get_link)
    print(len(get_link))
scrap_data()



