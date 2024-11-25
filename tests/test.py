from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    rating = None
    price_types = []

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

        if" - " in period:
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

    # 가격 유형 추출
    try:
        price_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '가격')]/following-sibling::div/ul[@class='product_info_sublist']/li[@class='product_info_subitem']"))
        )
        price_list = []  # 가격 정보를 임시로 저장할 리스트
        for price_element in price_elements:
            try:
                # 가격 정보를 직접 추출
                price_text = price_element.text.strip()  # 가격 정보 전체를 가져옴
                price_list.append(price_text)  # 리스트에 추가
            except Exception as e:
                print(f"가격 추출 실패: {e}")
        
        # 리스트를 문자열로 결합
        price = ", ".join(price_list)  # 가격 정보를 문자열로 결합
    except TimeoutException:
        print("가격 정보를 찾을 수 없습니다.")

    # 출력
    print("장소:", location)
    print("관람시간:", running_time)
    print("시작일:", start_date)
    print("종료일:", end_date)
    print("기간:", period)
    print("관람등급:", rating)
    print("가격 유형:", price)

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    driver.quit()
