import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# 현재 실행 중인 디렉토리 경로 가져오기
current_directory = os.getcwd()

# CSV 파일 경로를 현재 디렉토리로 설정
csv_filename = os.path.join(current_directory, "valid_links.csv")
html_filename = os.path.join(current_directory, "html.csv")

# 기본 URL 설정
base_url = "https://www.ticketlink.co.kr/help/notice/"

# 기존 CSV 파일에서 이미 처리된 csoonID 확인
csv_filename = "valid_links.csv"
html_filename = "html.csv"
processed_ids = set()

# valid_links.csv에서 처리된 ID 추가
try:
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            processed_ids.add(int(row["csoonID"]))
except FileNotFoundError:
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["csoonID", "Type", "ReservNum"])  # 헤더 작성

# html.csv에서도 처리된 ID 추가
try:
    with open(html_filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            processed_ids.add(int(row["csoonID"]))
except FileNotFoundError:
    with open(html_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["csoonID", "HTML"])  # 헤더 작성

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # GUI 없이 실행
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# csoonID를 반복하며 링크 검사
try:
    for csoonID in range(45228, 60838):  # 적절한 범위로 설정
        if csoonID in processed_ids:
            print(f"csoonID: {csoonID} 이미 처리됨. 건너뜀.")
            continue  # 이미 처리된 경우 건너뛰기

        current_url = f"{base_url}{csoonID}"
        try:
            driver.get(current_url)

            type_value = None
            reserv_num = None
            dl_list_view = None

            try:
                # dl.list_view HTML 긁어오기
                dl_list_view = driver.find_element(By.CLASS_NAME, "list_view").get_attribute("outerHTML")
                type_value = "HTML"  # 기본값 설정
                print(f"csoonID: {csoonID}, HTML 추출 완료")

                # btn_reserve 클래스 확인
                last_dd = driver.find_element(By.CLASS_NAME, "th_info").find_elements(By.TAG_NAME, "dd")[-1]
                btn_reserve = last_dd.find_elements(By.CLASS_NAME, "btn_reserve")

                if btn_reserve:
                    reserve_link = btn_reserve[0].get_attribute("href")
                    reserv_num = reserve_link.split("/")[-1]
                    type_value = "Link"  # 예매 링크 존재 시 Type 업데이트
                    print(f"csoonID: {csoonID}, 예매 링크 고유번호: {reserv_num}")

            except NoSuchElementException:
                print(f"csoonID: {csoonID}, 데이터 없음")

            # valid_links.csv와 html.csv에 데이터 저장 (데이터가 있을 때만)
            if type_value:
                with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([csoonID, type_value, reserv_num])

                # html.csv에 csoonID와 HTML 저장 (HTML 데이터가 있을 때만)
                if dl_list_view:
                    with open(html_filename, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([csoonID, dl_list_view])

                # 처리된 ID 목록에 추가
                processed_ids.add(csoonID)

        except WebDriverException as e:
            print(f"WebDriverException for csoonID: {csoonID} - {e}")
finally:
    driver.quit()

print(f"크롤링 완료! 결과는 {csv_filename}와 {html_filename}에 저장되었습니다.")
