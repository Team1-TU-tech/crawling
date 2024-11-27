from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time

# 상세예매링크에서 ['location', 'running_time', 'start_date', 'end_date', 'rating', 'price'] 정보 추출
def extract_performance_data(driver):

    data = {
        "location": None,
        "running_time": None,
        "start_date": None,
        "end_date": None,
        "rating": None,
        "price": None,
    }

    try:
        # location
        location_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '장소')]/following-sibling::div"
        location_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, location_xpath)))
        data["location"] = location_element.text.strip()

        # running time
        running_time_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '관람시간')]/following-sibling::div"
        running_time_element = driver.find_element(By.XPATH, running_time_xpath)
        data["running_time"] = running_time_element.text.strip()

        # period
        period_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '기간')]/following-sibling::div"
        period_element = driver.find_element(By.XPATH, period_xpath)
        period = period_element.text.strip()
        if " - " in period:
            data["start_date"], data["end_date"] = [d.strip() for d in period.split(" - ")]
        else:
            data["start_date"] = data["end_date"] = period.strip()

        # rating
        rating_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '관람등급')]/following-sibling::div"
        rating_element = driver.find_element(By.XPATH, rating_xpath)
        data["rating"] = rating_element.text.strip()

        # price
        price_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '가격')]/following-sibling::div/ul[@class='product_info_sublist']/li[@class='product_info_subitem']"
        price_elements = driver.find_elements(By.XPATH, price_xpath)
        prices = [elem.text.strip() for elem in price_elements]
        data["price"] = ", ".join(prices)

    except NoSuchElementException as e:
        print(f"데이터를 찾을 수 없습니다: {e}")
    except TimeoutException as e:
        print(f"시간 초과로 데이터를 가져오지 못했습니다: {e}")
    except Exception as e:
        print(f"기타 오류 발생: {e}")
    return data

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
            cast_data.append({'name': None, 'role': None})
            artist_data.append({'artist': None, 'artist_url': None})

        for cast in cast_list:
            try:
                # 캐스트 이미지 URL과 이름, 역할 추출
                img_url = cast.find_element(By.CLASS_NAME, 'product_casting_imgbox').find_element(By.TAG_NAME, 'img').get_attribute('src')
                name = cast.find_element(By.CLASS_NAME, 'product_casting_name').text.strip() if cast.find_element(By.CLASS_NAME, 'product_casting_name').text.strip() else None
                role = cast.find_element(By.CLASS_NAME, 'product_casting_role').text.strip() if cast.find_element(By.CLASS_NAME, 'product_casting_role').text.strip() else None

                # 캐스트 정보와 아티스트 정보를 중복 없이 저장
                if name or role:  # name이나 role이 None이 아닐 때만 추가
                    if {'name': name, 'role': role} not in cast_data:
                        cast_data.append({'name': name, 'role': role})
                    if {'artist': name, 'artist_url': img_url} not in artist_data:
                        artist_data.append({'artist': name, 'artist_url': img_url})
            except NoSuchElementException:
                # 예외 발생 시 None 값으로 추가
                cast_data.append({'name': None, 'role': None})
                artist_data.append({'artist': None, 'artist_url': None})

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
        cast_data.append({'name': None, 'role': None})
        artist_data.append({'artist': None, 'artist_url': None})

    return cast_data, artist_data

# 예매링크의 전체 HTML 추출
def extract_detail_html(driver):

    try:
        # 현재 페이지 HTML 가져오기
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # HTML 공백이 너무 많아서 처리
        minified_html = soup.prettify(formatter="minimal").replace("\n", "").strip()
        return minified_html
    
    except Exception as e:
        print(f"HTML 처리 중 오류 발생: {e}")
        return None
