import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from urllib3.exceptions import ReadTimeoutError

# Chrome WebDriver 설정 (ChromeDriver가 설치되어 PATH에 포함되어 있어야 합니다)
driver = webdriver.Chrome()

# 크롤링할 기본 URL 설정
base_url = "https://www.ticketlink.co.kr/help/notice/"

# HTML 저장 디렉토리 설정, 테스트용
html_save_directory = os.path.join(os.getcwd(), "html_files")
os.makedirs(html_save_directory, exist_ok=True)  # 디렉토리가 없으면 생성

# 유효한 링크 데이터(공연고유번호)를 저장할 빈 리스트 초기화
valid_links = []

# 크롤링 끝나는 범위 고유번호 추출 
def last_id(driver, base_url):
    try:
        driver.get(base_url)  # 기본 URL로 이동
        first_tr = driver.find_element(By.ID, "nTableBody").find_element(By.TAG_NAME, "tr")
        first_link = first_tr.find_element(By.CLASS_NAME, "tl.p_reative").find_element(By.TAG_NAME, "a")
        href = first_link.get_attribute("href")
        last_id = int(href.split("/")[-1])  # / 기준으로 마지막 값 추출
        return last_id
    except NoSuchElementException:
        print("마지막 고유번호를 찾을 수 없습니다.")
        return None

def process_csoon_page(driver, csoonID):
    """csoonID 페이지를 처리하여 데이터 저장."""
    current_url = f"{base_url}{csoonID}"
    try:
        driver.get(current_url)
        dl_list_view = driver.find_element(By.CLASS_NAME, "list_view").get_attribute("outerHTML")
        
        # 카테고리(th 값) 확인
        try:
            th_element = driver.find_element(By.CLASS_NAME, "th")
            th_value = th_element.text.strip()
        except NoSuchElementException:
            th_value = "공연"  # 기본값으로 "공연" 설정

        # btn_reserve 클래스에서 공연 고유번호 추출
        try:
            last_dd = driver.find_element(By.CLASS_NAME, "th_info").find_elements(By.TAG_NAME, "dd")[-1]
            btn_reserve = last_dd.find_elements(By.CLASS_NAME, "btn_reserve")
            show_id = btn_reserve[0].get_attribute("href").split("/")[-1] if btn_reserve else None
        except NoSuchElementException:
            show_id = None

        # 카테고리가 "공연"일 때만 저장
        if th_value == "공연":
            print(f"csoonID: {csoonID} / 카테고리: {th_value} / 고유번호: {show_id} / HTML 저장완료")

            # HTML 저장
            html_filename = os.path.join(html_save_directory, f"{csoonID}.html")
            with open(html_filename, mode='w', encoding='utf-8') as html_file:
                html_file.write(dl_list_view)

        else:
            print(f"csoonID: {csoonID}, 카테고리: {th_value} / >>넘어갑니다<<")

    except NoSuchElementException:
        print(f"사이트를 찾을 수 없음: {current_url}")
    except (WebDriverException, ReadTimeoutError) as e:
        print(f"오류 발생 (csoonID: {csoonID}): {e}")


def crawl_tickets(driver, base_url, start_id, last_id):
    """주어진 ID 범위 내에서 티켓 페이지 크롤링."""
    for csoonID in range(start_id, last_id + 1):
        process_csoon_page(driver, csoonID)

driver.quit()