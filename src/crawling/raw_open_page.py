from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup  # HTML 포맷팅을 위한 라이브러리
from webdriver_manager.chrome import ChromeDriverManager
from open_page_url import get_open_page_url
import time
import os


def extract_open_html(base_file_number):
    # ChromeOptions 객체 생성
    options = Options()
    options.add_argument("--no-sandbox")  # 추가한 옵션
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # 추가한 옵션
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--start-maximized")

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 크롤링 대상 URL
    #open_page_lists = get_open_page_url(49609,100)
    open_page_lists = get_open_page_url(baser_file_number,500)
    
    num = ''
    crawling_list=[]
    try:
        for page in open_page_lists:
            print(f"{page} 접속 중...")
            driver.get(page)
            num = page.split("groupno=")[1].split("&")[0]

            try:
                # `notice_detail` 클래스 요소가 로드될 때까지 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "notice_detail"))
                )

                # `notice_detail` 클래스 요소 찾기
                notice_detail_element = driver.find_element(By.CLASS_NAME, "notice_detail")
                # 내부 HTML 가져오기
                inner_html = notice_detail_element.get_attribute("outerHTML")
                # BeautifulSoup으로 HTML 포맷팅
                soup = BeautifulSoup(inner_html, "html.parser")
                crawling_list.append({"data":soup, "num":num})
                print(f"{num} 저장 완료")
                 
            except Exception as e:
                print(f"html 추출 중 오류 발생: {e}")
                continue    
            
    except Exception as e:
                print(f"오픈공지 접속 에러 : {e}")

    finally:
          driver.quit()

    return crawling_list

if __name__ == "__main__":
    # 함수 실행
    extract_open_html()

