import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from crawling.links import get_link  # 링크를 가져오는 함수
from crawling.utils import set_offset

def all_scrap():
    # Chrome 드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저를 띄우지 않고 실행
    options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 사용 비활성화
    options.add_argument('--no-sandbox')  # 샌드박스 모드 비활성화 (Docker 환경에서 권장)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    all_links = ['http://ticket.yes24.com/Perf/51671']
    #all_links = get_link(driver)
    title = ''
    for link in all_links:
        print(f"링크 수집 중: {link}")

        # 페이지 열기
        driver.get(link)

        # 페이지 로딩 대기 (WebDriverWait 사용)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'renew-content')))
        
        except Exception as e:
            print(f"페이지 로딩 실패: {e}")
            continue  
        
        title = link 

        try:
            # 페이지에서 특정 조건 확인
            category = driver.find_element(By.CSS_SELECTOR, '.rn-location a').text
            date = driver.find_element(By.CSS_SELECTOR, '.ps-date').text  # 시작일자와 종료일자가 포함된 텍스트
            start_date, end_date = date.split('~')  # '~'를 기준으로 시작일자와 종료일자 분리
            
            if category not in ['전시/행사', '콘서트', '뮤지컬', '연극'] or start_date[:4] != '2024':
                print(f"조건에 맞지 않는 페이지: {category}, 연도: {start_date}")
                continue

            # 전체 페이지 HTML 소스를 가져오기
            page_source = driver.page_source
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            raw_content = soup.find_all(class_="renew-content")
            print(raw_content)       

        except Exception as e:
            print(f"페이지에서 오류 발생: {e}")
            continue  # 오류가 발생해도 계속해서 다음 링크를 크롤링

    # 크롬 드라이버 종료
    driver.quit()
    
    return [raw_content, title] 

# 실행
if __name__ == "__main__":
    all_scrap = all_scrap()
