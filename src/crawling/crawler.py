import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from links import get_link  # 링크를 가져오는 함수
from utils import set_offset 

def scrap_data():
    # Chrome 드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저를 띄우지 않고 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    all_links = get_link(driver)
    #all_links = ['http://ticket.yes24.com/Perf/51651']
    
    # 크롤링할 데이터 저장용 리스트
    data = []

    for link in all_links:
        print(f"크롤링 중: {link}")

        # 페이지 열기
        driver.get(link)

        # 페이지 로딩 대기 (WebDriverWait 사용)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'rn-big-title')))
        except Exception as e:
            print(f"페이지 로딩 실패: {e}")
            continue  

        try:
            category = driver.find_element(By.CSS_SELECTOR, '.rn-location a').text if driver.find_elements(By.CSS_SELECTOR, '.rn-location a') else None # 카테고리
            exclusive_sales = driver.find_element(By.CSS_SELECTOR, '.rn-label').text if driver.find_element(By.CSS_SELECTOR, '.rn-label') else None #단독판매 여부
            title = driver.find_element(By.CLASS_NAME, 'rn-big-title').text if driver.find_element(By.CLASS_NAME, 'rn-big-title') else None # 공연 제목
            
            #date와 time 구분
            show_time = driver.find_element(By.CSS_SELECTOR, '.rn-product-area3 dd').text if driver.find_element(By.CSS_SELECTOR, '.rn-product-area3 dd') else None # 공연일자
            date = driver.find_element(By.CSS_SELECTOR, '.ps-date').text  # 시작일자와 종료일자가 포함된 텍스트
            start_date, end_date = date.split('~')  # '~'를 기준으로 시작일자와 종료일자 분리
            
            performance_details = driver.find_elements(By.CSS_SELECTOR, '.rn08-tbl td')
            running_time = performance_details[5].text if performance_details[5] else None # 공연시간
            age_rating = performance_details[4].text if performance_details[4] else None # 관람등급
            performance_place = performance_details[6].text if performance_details[6] else None # 공연장소
            
            # 가격정보 (없으면 None)
            price_elements = driver.find_elements(By.CSS_SELECTOR, '#divPrice .rn-product-price1')
            price = price_elements[0].text if price_elements else None
            poster_img = driver.find_element(By.CSS_SELECTOR, '.rn-product-imgbox img').get_attribute('src') if driver.find_element(By.CSS_SELECTOR, '.rn-product-imgbox img') else None # 포스터 이미지 URL
            benefits = driver.find_element(By.CSS_SELECTOR, '.rn-product-dc').text if driver.find_element(By.CSS_SELECTOR, '.rn-product-dc') else None # 혜택 및 할인 정보
            performers = driver.find_elements(By.CSS_SELECTOR, '.rn-product-peole') 

            performer_names = []
            performer_links = []

            # 출연진이 있을 경우, 이름과 링크를 분리하여 각각 추출
            for performer in performers:
                performer_names.append(performer.text)  # 이름만 추출
                performer_links.append(performer.get_attribute('href'))  # 링크만 추출

            # 출연진이 없을 경우 빈 리스트 사용
            if not performer_names:
                performer_names.append(None)
                performer_links.append(None)

            # 호스팅 서비스 사업자 정보
            hosting_provider = driver.find_element(By.CSS_SELECTOR, '.footxt p').text if driver.find_element(By.CSS_SELECTOR, '.footxt p').text else None
            organizer_info = driver.find_element(By.CSS_SELECTOR, '#divPerfOrganization').text if driver.find_element(By.CSS_SELECTOR, '#divPerfOrganization') else None

            # 데이터를 리스트에 추가
            data.append({
                'title':title,
                'category': category,
                'location': performance_place,
                'price': price,
                'start_date': start_date,
                'end_date': end_date,
                'show_time': show_time,
                'running_time': running_time,
                'casting': None,
                'rating': age_rating,
                'description': None,
                'poster_url': poster_img,
                'open_date': None,
                'pre_open_date': None,
                'hosts': {'host_name': hosting_provider, 'link': link, 'site_id': 2},
                'artist': performer_names,
                'artist_url': performer_links,
                })
            print(data)
        except Exception as e:
            print(f"페이지에서 오류 발생: {e}")
            continue  # 오류가 발생해도 계속해서 다음 링크를 크롤링

    # 크롬 드라이버 종료
    driver.quit()

    return data

# 실행
if __name__ == "__main__":
    scrap_data = scrap_data()
