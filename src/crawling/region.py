from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_location(location):
    # 지역 맵
    region_map = {
        '서울': '서울',
        '경기': '수도권',
        '인천': '수도권',
        '부산': '경상',
        '대구': '경상',
        '울산': '경상',
        '경남': '경상',
        '경북': '경상',
        '전북': '전라',
        '전주': '전라',
        '광주': '전라',
        '전남': '전라',
        '충남': '충청',
        '충북': '충청',
        '대전': '충청',
        '강원': '강원',
    }

    # ChromeOptions 객체 생성
    options = Options()
    # Headless 모드 활성화
    options.add_argument("--no-sandbox")  # 추가한 옵션
    #options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # 추가한 옵션
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    link = f'https://map.kakao.com/?q={location}'
    try:
        driver.get(link)

        # 페이지 로딩 기다리기 (예: 주소가 로딩될 때까지 기다림)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-id='address']"))
        )

        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # p 태그에서 data-id='address'를 찾고, 텍스트 추출
        address_tag = soup.find('p', {'data-id': 'address'})
        if address_tag:
            address_text = address_tag.get_text().strip()  # 텍스트 추출
            print("주소:", address_text)

            # 지역 추출 및 매핑
            region = None
            for region_key in region_map:
                if region_key in address_text:
                    region = region_map[region_key]
                    break

            if region:
                print(f"해당 지역은 {region}입니다.")
                return region
            else:
                print("지역을 찾을 수 없습니다.")
        else:
            print("주소를 찾을 수 없습니다.")

    except Exception as e:
        print(f"접속 에러: {e}")
    finally:
        driver.quit()  # 브라우저 종료

get_location("고척돔")