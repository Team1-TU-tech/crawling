from selenium import webdriver

def crawler(url_path=""):
    driver = webdriver.Chrome()

    driver.get(f"https://www.ticketlink.co.kr/help/notice/{url_path}")
    data = driver.page_source

    return data