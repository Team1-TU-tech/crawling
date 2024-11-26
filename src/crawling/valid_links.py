import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from urllib3.exceptions import ReadTimeoutError
from open_page import *
from offset import *

# 설정 상수
base_url = "https://www.ticketlink.co.kr/help/notice/"
html_dir = os.path.join(os.getcwd(), "html_files")

# 디렉토리 생성 함수
def setup_directories():
    os.makedirs(html_dir, exist_ok=True)  # HTML 파일 저장 디렉토리 생성
    return html_dir

# Selenium WebDriver 초기화
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

# 마지막 고유번호 추출 (크롤링 할 마지막 범위) 
def extract_last_id(driver, base_url):
    try:
        driver.get(base_url)
        first_tr = driver.find_element(By.ID, "nTableBody").find_element(By.TAG_NAME, "tr")
        first_link = first_tr.find_element(By.CLASS_NAME, "tl.p_reative").find_element(By.TAG_NAME, "a")
        href = first_link.get_attribute("href")
        last_id = int(href.split("/")[-1])  # / 기준으로 마지막 값 추출
        return last_id
    except NoSuchElementException:
        print("마지막 고유번호를 찾을 수 없습니다.")
        return None

# 오픈예정 페이지 크롤링 (1. 유효햔 (csoonID, showID) 2. 오픈예정페이지 html 저장)
def crawl_ID(driver, csoonID, html_save_directory, valid_links):
    current_url = f"{base_url}{csoonID}"
    try:
        driver.get(current_url)

        # 데이터 초기화
        dl_list_view = None
        showID = None
        th_value = None

        try:
            # HTML 데이터 추출
            dl_list_view = driver.find_element(By.CLASS_NAME, "list_view").get_attribute("outerHTML")

            # 카테고리 추출
            try:
                th_element = driver.find_element(By.CLASS_NAME, "th")
                th_value = th_element.text.strip()
            except NoSuchElementException:
                th_value = "공연"  # 기본값

            # 예매 링크 추출
            try:
                last_dd = driver.find_element(By.CLASS_NAME, "th_info").find_elements(By.TAG_NAME, "dd")[-1]
                btn_reserve = last_dd.find_elements(By.CLASS_NAME, "btn_reserve")

                if btn_reserve:
                    reserve_link = btn_reserve[0].get_attribute("href")
                    showID = reserve_link.split("/")[-1]  # 공연 고유번호 추출
            except NoSuchElementException:
                showID = None

            # 공연 데이터 저장
            if th_value == "공연":
                print(f"csoonID: {csoonID} / 카테고리: {th_value} / 고유번호: {showID} / HTML 저장완료")

                # 유효한 ID 저장
                valid_links.append({"csoonID": csoonID, "showID": showID})

##############html list####################
                # HTML 파일로 저장
                html_filename = os.path.join(html_save_directory, f"{csoonID}.html")
                with open(html_filename, mode='w', encoding='utf-8') as html_file:
                    html_file.write(dl_list_view)
            else:
                print(f"csoonID: {csoonID}, 카테고리: {th_value} / >>넘어갑니다<<")

        except NoSuchElementException:
            print(f"사이트를 찾을 수 없음: {current_url}")

    except (WebDriverException, ReadTimeoutError) as e:
        print(f"오류 발생 (csoonID: {csoonID}): {e}")

def collect_valid_links():

    driver = initialize_driver()
    html_save_directory = setup_directories()
    valid_links = []

    try:
        # 마지막 ID 가져오기
        last_id = extract_last_id(driver, base_url)
        if last_id is None:
            print("마지막 고유번호를 가져오지 못했습니다. 프로그램을 종료합니다.")
            return []   
    
        start_id = get_offset()

        # 크롤링 실행
        for csoonID in range(start_id, last_id + 1): #45228 #60850
            try:
                crawl_ID(driver, csoonID, html_save_directory, valid_links)
                # 유효한 링크 크롤링 후 offset 저장
                set_offset(csoonID + 1)
            except Exception as e:
                print(f"오류 발생하여 csoonID: {csoonID}에서 중단되었습니다. 오류: {e}")
                break  # 오류 발생 시 현재까지 크롤링된 ID를 저장하고 종료
    finally:
        driver.quit()
        print("크롤링 완료!")
        print(f"총 {len(valid_links)}개의 유효한 링크를 수집했습니다.")
        print(valid_links)
    return valid_links


def crawl_valid_links(valid_links):
    driver = initialize_driver()

    try:
        for link in valid_links:
            csoonID = link['csoonID']
            print(f"open_page 데이터 수집을 시작합니다: csoonID = {csoonID}")
            crawl_open_page(driver, csoonID) #open_page.py에서 import

    finally:
        driver.quit()
        print("추가 데이터 수집 완료!")

#####실행#####
valid_links = collect_valid_links()

if valid_links:
    crawl_valid_links(valid_links)
else:
    print("수집된 유효한 링크가 없습니다.")