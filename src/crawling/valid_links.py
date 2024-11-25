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

# 텍스트 파일 경로 설정
valid_links_filename = os.path.join(os.getcwd(), "valid_links.txt")

# 마지막 고유번호 추출 함수 (크롤링 범위)
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

try:
    # 티켓오픈 공지사항에서 맨 위에 있는 고유번호 (크롤링의 마지막 범위) 가져오기
    last_id = get_last_id_from_page(driver, base_url)
    if last_id is None:
        print("마지막 고유번호를 가져오지 못했습니다. 프로그램을 종료합니다.")
        driver.quit()
        exit()

    # 크롤링 시작
    for csoonID in range(45228, last_id + 1):  # 페이지 내에 있는 가장 마지막 고유번호까지만 추출 반복, 45228은 티켓오픈 첫 번호
        current_url = f"{base_url}{csoonID}"
        try:
            driver.get(current_url)

            dl_list_view = None
            show_id = None
            th_value = None

            try:
                # list_view HTML (티켓오픈예정의 raw data)
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
                    
                    # 유효한 링크 및 데이터 저장
                    valid_link_data = {
                        "csoonID": csoonID,
                        "showID": show_id,
                    }
                    valid_links.append(valid_link_data)

                    # 텍스트 파일에 저장 (중간에 중단되어도 데이터가 남도록) 
                    with open(valid_links_filename, mode='a', encoding='utf-8') as file:
                        file.write(f"csoonID: {csoonID}, showID: {show_id}\n")

                    # HTML 파일로 저장
                    html_filename = os.path.join(html_save_directory, f"{csoonID}.html")
                    with open(html_filename, mode='w', encoding='utf-8') as html_file:
                        html_file.write(dl_list_view)

                else:  # 스포츠, 변경/취소, 시스템, 기타 카테고리
                    print(f"csoonID: {csoonID}, 카테고리: {th_value} / >>넘어갑니다<<")
 
            except NoSuchElementException:
                print(f"사이트 찾을 수 없음: {current_url}")
                continue

        except (WebDriverException, ReadTimeoutError) as e:
            print(f"오류 발생 (csoonID: {csoonID}): {e}")
            continue

finally:
    driver.quit()

# 결과 출력
# print(f"크롤링 완료! 유효한 링크 데이터: {valid_links}")
# print(f"티켓오픈예정 HTML raw data: {dl_list_view}")