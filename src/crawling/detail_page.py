from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time

# Chrome WebDriver setup
driver = webdriver.Chrome()

# URL
url = "https://www.ticketlink.co.kr/product/52656"  # 예시 URL
driver.get(url)

try:
    # HTML 로드 대기
    wait = WebDriverWait(driver, 10)

    # 데이터 초기화
    location = None
    running_time = None
    period = None
    start_date = None
    end_date = None
    rating = None
    price = None
    cast_data = []
    artist_data = []

    # 장소
    try:
        location_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '장소')]/following-sibling::div"))
        )
        location = location_element.text.strip()
    except TimeoutException:
        print("장소 정보를 찾을 수 없습니다.")

    # 관람시간
    try:
        running_time_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '관람시간')]/following-sibling::div"))
        )
        running_time = running_time_element.text.strip()
    except TimeoutException:
        print("관람시간 정보를 찾을 수 없습니다.")

    # 기간
    try:
        period_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '기간')]/following-sibling::div"))
        )
        period = period_element.text.strip()

        if " - " in period:
            start_date, end_date = period.split(" - ")
        else:
            start_date = end_date = period.strip()

        start_date = start_date.strip()
        end_date = end_date.strip()
    except TimeoutException:
        print("기간 정보를 찾을 수 없습니다.")

    # 관람등급
    try:
        rating_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '관람등급')]/following-sibling::div"))
        )
        rating = rating_element.text.strip()
    except TimeoutException:
        print("관람등급 정보를 찾을 수 없습니다.")

    # 가격
    try:
        price_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '가격')]/following-sibling::div/ul[@class='product_info_sublist']/li[@class='product_info_subitem']"))
        )
        price_list = []
        for price_element in price_elements:
            try:
                # 가격 정보를 직접 추출
                price_text = price_element.text.strip()
                price_list.append(price_text)
            except Exception as e:
                print(f"가격 추출 실패: {e}")
        
        # 리스트를 문자열로 결합
        price = ", ".join(price_list)
    except TimeoutException:
        print("가격 정보를 찾을 수 없습니다.")

    # 출연진 정보
    try:
        time.sleep(3)  # HTML 로드 대기
        main_content = driver.find_element(By.CLASS_NAME, 'common_container.page_detail')

        while True:
            # 현재 페이지에서 모든 출연진 요소 찾기
            cast_list = main_content.find_elements(By.CLASS_NAME, 'product_casting_item')

            for cast in cast_list:
                try:
                    # 이미지 URL, 이름, 배역 추출
                    img_element = cast.find_element(By.CLASS_NAME, 'product_casting_imgbox').find_element(By.TAG_NAME, 'img')
                    img_url = img_element.get_attribute('src')

                    name = cast.find_element(By.CLASS_NAME, 'product_casting_name').text.strip()
                    role = cast.find_element(By.CLASS_NAME, 'product_casting_role').text.strip()

                    # cast_data와 artist_data 리스트에 이미 추가되지 않은 경우 데이터 추가
                    if {'name': name, 'role': role} not in cast_data:
                        cast_data.append({
                            'name': name,
                            'role': role
                        })
                    if {'artist': name, 'artist_url': img_url} not in artist_data:
                        artist_data.append({
                            'artist': name,
                            'artist_url': img_url
                        })
                except NoSuchElementException:
                    continue

            # 다음 버튼이 있는지 확인하고 클릭하여 더 많은 출연진 로드
            try:
                next_button = driver.find_element(By.CLASS_NAME, 'product_casting_nav.swiper-button-next.casting-list-swiper-next')
                if next_button.is_enabled():
                    ActionChains(driver).move_to_element(next_button).click(next_button).perform()
                    time.sleep(1)  # 약간의 지연
                else:
                    break
            except NoSuchElementException:
                # 다음 버튼을 찾을 수 없으면 루프 종료
                break
    except NoSuchElementException:
        print("출연진 정보를 찾을 수 없습니다.")

    # HTML 저장 (공백 제거)
    try:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        minified_html = soup.prettify(formatter="minimal").replace("\n", "").strip()

        # 파일 저장
        output_file = "minified_ticketlink.html"
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(minified_html)

        print(f"HTML이 공백 없이 '{output_file}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"HTML 저장 중 오류 발생: {e}")

    # 데이터 출력
    print("장소:", location)
    print("관람시간:", running_time)
    print("시작일:", start_date)
    print("종료일:", end_date)
    print("기간:", period)
    print("관람등급:", rating)
    print("가격:", price)
    print("Cast Data:", cast_data)
    print("Artist Data:", artist_data)

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    driver.quit()
