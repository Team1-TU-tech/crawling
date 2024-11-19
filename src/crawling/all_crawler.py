import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from links import get_link  # 링크를 가져오는 함수
from utils import set_offset

def all_scrape_data():
    # Chrome 드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저를 띄우지 않고 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    #all_links = ['http://ticket.yes24.com/Perf/51733']
    all_links = get_link(driver)
    
    for link in all_links:
        print(f"크롤링 중: {link}")

        # 페이지 열기
        driver.get(link)

        # 페이지 로딩 대기 (WebDriverWait 사용)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'renew-content')))
        
        except Exception as e:
            print(f"페이지 로딩 실패: {e}")
            continue  

        try:
            # 전체 페이지 HTML 소스를 가져오기
            page_source = driver.page_source

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            renew_content = soup.find_all(class_="renew-content")

            # 데이터를 출력
            for content in renew_content:
                print(content.text)

        except Exception as e:
            print(f"페이지에서 오류 발생: {e}")
            continue  # 오류가 발생해도 계속해서 다음 링크를 크롤링

    # 크롬 드라이버 종료
    driver.quit()

    return content.text 

# 실행
if __name__ == "__main__":
    all_scraped_data = all_scrape_data()
