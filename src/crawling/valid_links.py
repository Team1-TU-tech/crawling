from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from urllib3.exceptions import ReadTimeoutError
from bs4 import BeautifulSoup
from open_page import *
from offset import *

base_url = "https://www.ticketlink.co.kr/help/notice/"


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
        print("마지막 고유번호를 찾을 수 없습니다. 기본값(62000)으로 설정합니다.")
        return 62000 
    except ValueError as e:
        print(f"고유번호를 추출할 수 없습니다. 기본값(62000)으로 설정합니다. 오류: {e}")
        return 62000  
    except Exception as e:
        print(f"예기치 못한 오류 발생: {e}. 기본값(62000)으로 설정합니다.")
        return 62000 
    
# 오픈예정 페이지 크롤링 (1. 유효햔 (csoonID, showID) 2. 오픈예정/디테일 페이지 html 저장)
def crawl_ID(driver, csoonID, valid_links):
    current_url = f"{base_url}{csoonID}"
    try:
        driver.get(current_url)

        # 데이터 초기화
        showID = None
        th_value = None

        try:

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
                print(f"csoonID: {csoonID} / 카테고리: {th_value} / 고유번호: {showID} ")

                # 유효한 ID 저장
                valid_links.append({"csoonID": csoonID, "showID": showID})

            else:
                print(f"csoonID: {csoonID}, 카테고리: {th_value} / >>넘어갑니다<<")

        except NoSuchElementException:
            print(f"사이트를 찾을 수 없음: {current_url}")
        except Exception as e:
            print(f"데이터 처리 중 오류 발생 (csoonID: {csoonID}): {e}")

    except WebDriverException as e:
        print(f"웹 드라이버 오류 발생 (csoonID: {csoonID}): {e}")
    except ReadTimeoutError as e:
        print(f"페이지 로드 시간 초과 (csoonID: {csoonID}): {e}")
    except Exception as e:
        print(f"예기치 못한 오류 발생 (csoonID: {csoonID}): {e}")
def collect_valid_links():

    driver = initialize_driver()
    valid_links = []

    try:
        # 마지막 ID 가져오기
        # last_id = extract_last_id(driver, base_url)
        # if last_id is None:
        #     print("마지막 고유번호를 가져오지 못했습니다. 프로그램을 종료합니다.")
        #     return []   
    
        # start_id = get_offset()
        start_id = 60858
        last_id = 60860
        # start_id = 45255
        # last_id = 45257

        # 크롤링 실행
        for csoonID in range(start_id, last_id + 1): 
            try:
                crawl_ID(driver, csoonID, valid_links)
                # 유효한 링크 크롤링 후 offset 저장
                #set_offset(csoonID + 1)
            except Exception as e:
                print(f"오류 발생하여 csoonID: {csoonID}에서 중단되었습니다. 오류: {e}")
                continue  # 현재 ID를 건너뛰고 다음 ID로 진행
    finally:
        driver.quit()
        print(f"*****valid links 저장 완료!***** / 총 {len(valid_links)}개의 유효한 링크를 수집했습니다.")
        print(valid_links)
    return valid_links

