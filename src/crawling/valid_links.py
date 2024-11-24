import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from urllib3.exceptions import ReadTimeoutError

# 현재 실행 중인 디렉토리 경로 가져오기
current_directory = os.getcwd()

# CSV 파일 경로를 현재 디렉토리로 설정
csv_filename = os.path.join(current_directory, "open_info.csv")
error_filename = os.path.join(current_directory, "error_log.csv")

# 기본 URL 설정
base_url = "https://www.ticketlink.co.kr/help/notice/"

# 기존 파일에서 마지막 csoonID 읽기
def get_last_processed_id(filename):
    last_id = 45227
    if os.path.exists(filename):
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # 헤더 건너뛰기
                for row in reader:
                    last_id = max(last_id, int(row[0]))  # csoonID는 첫 번째 열
        except Exception as e:
            print(f"{filename}에서 마지막 ID 읽기 실패: {e}")
    return last_id

# 마지막 고유번호 추출 함수
def get_last_id_from_page(driver, base_url):
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

# Selenium WebDriver 설정 및 크롤링 로직
options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

try:
    # nTableBody의 첫 번째 고유번호 가져오기
    last_id = get_last_id_from_page(driver, base_url)
    if last_id is None:
        print("마지막 고유번호를 가져오지 못했습니다. 프로그램을 종료합니다.")
        driver.quit()
        exit()

    # 파일에 헤더 추가 (파일이 없는 경우)
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["csoonID", "showID", "HTML"])

    # 파일에 헤더 추가 (error_log.csv)
    if not os.path.exists(error_filename):
        with open(error_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["csoonID", "Error"])

    # 기존 파일에서 마지막으로 처리된 ID 가져오기
    offset = get_last_processed_id(csv_filename) + 1
    print(f"csoonID: {offset - 1}까지 저장되어 있습니다.\n{offset} 부터 {last_id}까지 추출을 시작합니다.")

    # 크롤링 시작
    for csoonID in range(offset, last_id + 1):  # 페이지 내에 있는 가장 마지막 고유번호까지만 추출 반복
        current_url = f"{base_url}{csoonID}"
        try:
            driver.get(current_url)

            dl_list_view = None
            show_id = None
            th_value = None

            try:
                # list_view HTML 긁어오기
                dl_list_view = driver.find_element(By.CLASS_NAME, "list_view").get_attribute("outerHTML")
                
                # 카테고리(th 값) 확인
                try:
                    th_element = driver.find_element(By.CLASS_NAME, "th")
                    th_value = th_element.text.strip()
                except NoSuchElementException:
                    th_value = "공연"  # th 값이 없으면 "공연"으로 설정

                # btn_reserve 클래스 확인
                try:
                    last_dd = driver.find_element(By.CLASS_NAME, "th_info").find_elements(By.TAG_NAME, "dd")[-1]
                    btn_reserve = last_dd.find_elements(By.CLASS_NAME, "btn_reserve")

                    if btn_reserve:
                        reserve_link = btn_reserve[0].get_attribute("href")
                        show_id = reserve_link.split("/")[-1]  # 공연 고유 번호 추출
                    else:
                        show_id = None

                except NoSuchElementException:
                    show_id = None

                # 카테고리에 따른 데이터 처리
                if th_value == "공연":  # 공연 카테고리
                    print(f"csoonID: {csoonID} / 카테고리: {th_value} / 고유번호: {show_id} / HTML 저장완료")
                    
                    # open_info.csv 저장
                    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([csoonID, show_id, dl_list_view])

                else:  # 스포츠, 변경/취소, 시스템, 기타 카테고리
                    print(f"csoonID: {csoonID}, 카테고리: {th_value} / >>넘어갑니다<<")
 
            except NoSuchElementException:
                print(f"사이트 찾을 수 없음: {current_url}")
                continue

        except (WebDriverException, ReadTimeoutError) as e:
            print(f"오류 발생 (csoonID: {csoonID}): {e}")
            with open(error_filename, mode='a', newline='', encoding='utf-8') as error_file:
                writer = csv.writer(error_file)
                writer.writerow([csoonID, str(e)])
            continue

finally:
    driver.quit()

print(f"크롤링 완료! 결과는 {csv_filename}에 저장되었습니다.")
