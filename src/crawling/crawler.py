from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crawling.page_down import page_down
import re

def crawling_data():
    # Chrome 드라이버 설정
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  # 브라우저를 띄우지 않고 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    a_list = []
    for num in range(5):
    # 공연 페이지 열기
        url = f'http://ticket.yes24.com/New/Genre/GenreList.aspx?genretype=1&genre={15456 + num}'
        driver.get(url)

        page_down(driver, time)
        time.sleep(3)
        
        div_info = driver.find_elements(By.CSS_SELECTOR, '.ms-list-imgs a')

        li_test = []
        list_cnt = driver.find_element(By.CSS_SELECTOR,'#ListCntText').text
        
        if len(div_info) != int(list_cnt[:-1]):
            page_down(driver, time)
        
        time.sleep(2)
        div_info = driver.find_elements(By.CSS_SELECTOR, '.ms-list-imgs a')
        
        for on_click_info in div_info:
            li_test.append(on_click_info.get_attribute('onClick'))
        
        numbers = [re.search(r'\d+', item).group() for item in li_test]
        a_list = a_list + numbers
    
    url = f'http://ticket.yes24.com/New/Genre/GenreList.aspx?genretype=1&genre=999'
    driver.get(url)

    page_down(driver, time)
    time.sleep(3)
    div_info = driver.find_elements(By.CSS_SELECTOR, '.ms-list-imgs a')

    perf_list = []
    list_cnt = driver.find_element(By.CSS_SELECTOR,'#ListCntText').text
    
    
    if len(div_info) != int(list_cnt[:-1]):
        page_down(driver, time)
    
    time.sleep(2)
    div_info = driver.find_elements(By.CSS_SELECTOR, '.ms-list-imgs a')
    for on_click_info in div_info:
        perf_list.append(on_click_info.get_attribute('onClick'))
    
    
    numbers = [re.search(r'\d+', item).group() for item in perf_list]
    a_list = a_list + numbers
    print(len(a_list))
    get_link = [f'http://ticket.yes24.com/Perf/{id}' for id in a_list]
    print(len(get_link))

    return get_link

crawling_data()