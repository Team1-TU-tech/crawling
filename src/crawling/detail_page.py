from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re

def get_location(location, max_retries=1):
    # 지역 맵
    region_map = {
        '서울': '서울',
        '경기': '수도권',
        '인천': '수도권',
        '세종': '수도권',
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
        '제주': '제주'
    }

    # ChromeOptions 객체 생성
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")  # 필요 시 활성화
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")

    retries = 0  # 재시도 횟수 초기화
    
    # location 값 확인
    if not location:  # location이 None 또는 빈 문자열이면
        print("location 값이 없습니다. 작업을 중단합니다.")
        return None
    
    link = f'https://map.kakao.com/?q={location}'

    while retries < max_retries:
        try:
            # WebDriver 객체 생성
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(link)

            # 페이지 로딩 기다리기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-id='address']"))
            )

            # 현재 URL이 404인지 확인
            if "404.ko.html" in driver.current_url:
                print(f"404 페이지 탐지. 재시도 중... ({retries + 1}/{max_retries})")
                retries += 1
                driver.quit()  # 브라우저 종료
                time.sleep(1)  # 대기 후 재시도
                continue

            # 페이지 소스 가져오기
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # p 태그에서 data-id='address'를 찾고, 텍스트 추출
            address_tag = soup.find('p', {'data-id': 'address'})
            if address_tag:
                address_text = address_tag.get_text().strip()  # 텍스트 추출
                #print("주소:", address_text)

                # 지역 추출 및 매핑
                region = None
                for region_key in region_map:
                    if region_key in address_text:
                        region = region_map[region_key]
                        break

                driver.quit()  # 브라우저 종료
                if region:
                    #print(f"해당 지역은 {region}입니다.")
                    return region
                else:
                    #print("지역을 찾을 수 없습니다.")
                    return None
            else:
                #print("주소를 찾을 수 없습니다.")
                driver.quit()  # 브라우저 종료
                return None

        except TimeoutException:
            print(f"Timeout 발생. 재시도 중... ({retries + 1}/{max_retries})")
            retries += 1
            time.sleep(1)  # 대기 후 재시도

        except Exception as e:
            print(f"에러 발생: {e}")
            return None

        finally:
            if 'driver' in locals():  # 드라이버가 생성되었는지 확인
                driver.quit()

    # 최대 재시도 초과 시
    print("최대 재시도 횟수 초과. 작업을 종료합니다.")
    return None

   
def crawl_region(location, max_retries=1):
    attempt = 0  # 전체 반복 횟수
    while attempt < max_retries:
        if not location:  # location이 None인지 확인
            print("location 값이 None입니다. 작업을 중단합니다.")
            return None

        # region 시도
        region = get_location(location)
        if region:
            print(f"지역: {region}")
            return region

        print(f"region 시도 실패: {attempt + 1}/{max_retries}")

        # location 값이 문자열인지 확인
        if isinstance(location, str):
            # strip (location 단순화)
            location_parts = location.rsplit(' ', 1)

            if len(location_parts) > 1:
                location = location_parts[0]  # 마지막 단어 제거
                print(f"단순화된 location으로 재시도: {location}")
            else:
                print("더 이상 단순화할 수 없는 location입니다.")
                break
        else:
            print("location 값이 문자열이 아닙니다.")
            break
        
        # 단순화된 location으로 다시 region 시도
        region = get_location(location)
        if region:
            print(f"단순화된 location으로 성공: {region}")
            return region

        print(f"단순화된 location도 실패: {attempt + 1}/{max_retries}")

        # 프로세스 반복
        attempt += 1

    print("최대 프로세스 반복 횟수를 초과했습니다.")
    return None


# 상세예매링크에서 ['location', 'running_time', 'start_date', 'end_date', 'rating', 'price'] 정보 추출
def extract_performance_data(driver):
    data = {
        "title": None,
        "location": None,
        "running_time": None,
        "start_date": None,
        "end_date": None,
        "rating": None,
        "price": None,
    }

    try:
        # title 추출
        try:
            title_xpath = "//h1[@class='product_title']"  # 예시로, 실제 title 위치에 맞게 수정 필요
            title_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, title_xpath)))
            data["title"] = title_element.text.strip()
        except Exception as e:
            print(f"title을 찾을 수 없습니다: {e}")

        # location 추출
        try:
            location_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '장소')]/following-sibling::div"
            location_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, location_xpath)))
            data["location"] = location_element.text.strip()
        except Exception as e:
            print(f"location을 찾을 수 없습니다: {e}")

        # running time 추출
        try:
            running_time_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '관람시간')]/following-sibling::div"
            running_time_element = driver.find_element(By.XPATH, running_time_xpath)
            data["running_time"] = running_time_element.text.strip()
        except Exception as e:
            print(f"running_time을 찾을 수 없습니다: {e}")

        # period 추출
        try:
            period_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '기간')]/following-sibling::div"
            period_element = driver.find_element(By.XPATH, period_xpath)
            period = period_element.text.strip()
            if " - " in period:
                data["start_date"], data["end_date"] = [d.strip() for d in period.split(" - ")]
            else:
                data["start_date"] = data["end_date"] = period.strip()
        except Exception as e:
            print(f"기간 정보를 찾을 수 없습니다: {e}")

        # rating 추출
        try:
            rating_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '관람등급')]/following-sibling::div"
            rating_element = driver.find_element(By.XPATH, rating_xpath)
            data["rating"] = rating_element.text.strip()
        except Exception as e:
            print(f"rating 정보를 찾을 수 없습니다: {e}")

        # price 추출
        try:
            price_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '가격')]/following-sibling::div/ul[@class='product_info_sublist']/li[@class='product_info_subitem']"
            price_elements = driver.find_elements(By.XPATH, price_xpath)
            prices = [elem.text.strip() for elem in price_elements]
            data["price"] = ", ".join(prices)

        except Exception as e:
            print(f"price 정보를 찾을 수 없습니다: {e}")




    except Exception as e:
        print(f"기타 오류 발생: {e}")

    return data


def extract_seat_prices(price):
    # 정규 표현식: 좌석과 가격을 추출
    pattern = r'([A-Za-z가-힣]+(?:석)?(?:\([^\)]+\))?)\s*[-]?\(?(\d{1,3}(?:,\d{3})*)\s*원\)?|(\d{1,3}(?:,\d{3})*)\s*원'
    
    result = []
    #seat = None 
    # '/'로 구분된 경우 처리

    # price가 None이면 빈 문자열로 처리
    if price is None:
        print("price 값이 None입니다. 빈 문자열로 대체합니다.")
        price = None
        price_list = []
    # '/'로 구분된 경우 처리
    else:
        price_list = price.split(' / ')
    
    for price_item in price_list:
        matches = re.findall(pattern, price_item.strip())
        
        if matches:
            for match in matches:
                
                if match[0] and match[1]:  # 좌석과 가격이 모두 있는 경우
                    seat = match[0].strip()
                    price = int(match[1].replace(",", ""))
                    price = "{:,.0f}".format(price)
                elif match[2]:  # 가격만 있는 경우
                    seat = '일반석'
                    price = int(match[2].replace(",", ""))
                    price = "{:,.0f}".format(price)
                
                price =  str(price)
                up_price = price.replace("원", "")
                up_price = up_price.strip() + "원"
                result.append({'seat': seat, 'price': up_price})
          
    return result
    
# 캐스팅 (이름, 역할) / 아티스트 (이름, 아티스트 url)
def extract_cast_data(driver):
    cast_data, artist_data = [], []
    try:
        time.sleep(3)  
        main_content = driver.find_element(By.CLASS_NAME, 'common_container.page_detail')

        # 캐스트 정보 추출
        cast_list = main_content.find_elements(By.CLASS_NAME, 'product_casting_item')
        if not cast_list:
            # 캐스트 정보가 없으면 None 값으로 기본 추가
            cast_data = [] 
            artist_data = [] 

        for cast in cast_list:
            try:
                # 캐스트 이미지 URL과 이름, 역할 추출
                img_url = cast.find_element(By.CLASS_NAME, 'product_casting_imgbox').find_element(By.TAG_NAME, 'img').get_attribute('src')
                actor = cast.find_element(By.CLASS_NAME, 'product_casting_name').text.strip() if cast.find_element(By.CLASS_NAME, 'product_casting_name').text.strip() else None
                role = cast.find_element(By.CLASS_NAME, 'product_casting_role').text.strip() if cast.find_element(By.CLASS_NAME, 'product_casting_role').text.strip() else None

                # 캐스트 정보와 아티스트 정보를 중복 없이 저장
                if actor or role:  # name이나 role이 None이 아닐 때만 추가
                    if {'role': role, 'actor': actor} not in cast_data:
                        cast_data.append({'role': role, 'actor': actor})
                    if {'artist_name': actor, 'artist_url': img_url} not in artist_data:
                        artist_data.append({'artist_name': actor, 'artist_url': img_url})
            except NoSuchElementException:
                # 예외 발생 시 None 값으로 추가
                cast_data = [] 
                artist_data = [] 

        # 캐스팅 정보가 많아서 다음 버튼이 있으면 누르기
        while True:
            try:
                next_button = driver.find_element(By.CLASS_NAME, 'product_casting_nav.swiper-button-next.casting-list-swiper-next')
                if next_button.is_enabled():
                    ActionChains(driver).move_to_element(next_button).click(next_button).perform()
                    time.sleep(1)
                else:
                    break
            except NoSuchElementException:
                break
    except NoSuchElementException:
        print("출연진 정보를 찾을 수 없습니다.")
        
        # 출연진 정보가 아예 없을 경우 None 값을 추가
        cast_data = [] 
        artist_data = []  
        
    return cast_data, artist_data
