from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

from interpark.open_page_url import get_open_page_url


def extract_ticket_html():
    # ChromeOptions 객체 생성
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.20 Safari/537.36");
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")  # headless 있으면 동작안됌
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu") 
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1920,1080")

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 크롤링 대상 URL
    open_page_lists = get_open_page_url(52610,5)
    #open_page_lists = get_open_page_url(53208,2)
    
    num = ''
    ticket_num =''
    crawling_list=[]

    try:
        for page in open_page_lists:
            print(f"{page} 접속 중...")
            driver.get(page)
            num = page.split("groupno=")[1].split("&")[0]

            try:
                # 페이지 로드 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "btn"))
                )
                # `btn` 클래스 내의 모든 링크 수집
                btn_element = driver.find_element(By.CLASS_NAME, "btn")
                a_elements = btn_element.find_elements(By.TAG_NAME, "a")

                # link 추출
                for a in a_elements:
                    href = a.get_attribute("href")
                    # 유효한 URL인지 확인
                    if href and 'http' in href:  
                        link = a.get_attribute("href")
                        ticket_num=link.split("/")[-1].split("?")[0]
                        print(ticket_num)

                        try:
                            book_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//a[@class='btn_book']"))
                            )
                            # 버튼 클릭
                            book_button.click()
                            # 모든 창 핸들 가져오기
                            window_handles = driver.window_handles
                            
                            # 새로 열린 창으로 전환
                            driver.switch_to.window(window_handles[-1])
                            # 페이지 작업 수행
                            print("현재 창 URL:", driver.current_url)
                            
                            try:
                                
                                WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "productMain"))
                                )
                                # productMain 하위의 모든 HTML 가져오기
                                product_html = driver.find_element(By.CLASS_NAME, "productMain").get_attribute('outerHTML')
                                soup = BeautifulSoup(product_html, "html.parser")
                                crawling_list.append({"data":soup, "num":num, "ticket_num":ticket_num})
                                print(f"{ticket_num} 저장 완료")
                            except Exception as e:

                                print(e)
                        
                        except Exception as e:
                            print(f"html 추출 중 오류 발생: {e}")
                            continue

            except Exception as e:
                print("페이지 로드 에러")
    
    except Exception as e:
                print(f"{page} 페이지 접속 에러: {e}")

    finally:
        driver.quit()
    
    return crawling_list

if __name__ == "__main__":
    # 함수 실행
    extract_ticket_html()

