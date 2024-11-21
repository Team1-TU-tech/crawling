
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# 테스트할 웹사이트 URL
test_url = "https://www.ticketlink.co.kr/help/notice/57930"  # 에스파
#test_url = "https://www.ticketlink.co.kr/help/notice/59062"  # 남주
#test_url = "https://www.ticketlink.co.kr/help/notice/59142"  # 베리베리
#test_url = "https://www.ticketlink.co.kr/help/notice/60826" #호두까기 인형

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 필요 시 헤드리스 모드 활성화
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

try:
    driver.get(test_url)

    # WebDriverWait 사용
    wait = WebDriverWait(driver, 10)

    # 데이터 초기화
    poster_url = None
    title = None
    ticket_link = None
    start_date = None
    end_date = None
    show_time = None
    location = None
    price = None
    running_time = None
    rating = None
    open_date = None
    pre_open_date = None

    ################## 전체 텍스트 추출 ##################
    # 페이지 소스의 모든 텍스트 가져오기
    page_text = driver.find_element(By.TAG_NAME, "body").text

    ################## 공연 정보 추출 ##################
    # 공연 일시
    match_date = re.search(r"공연\s*(일시|기간)\s*[:：]?\s*([^\n]+)", page_text)

    if match_date:
        full_date = match_date.group(2).strip()
        if " ~ " in full_date:  # 기간이 '~'로 구분되어 있는 경우
            start_date, end_date = full_date.split(" ~ ")
            start_date = start_date.strip()
            end_date = end_date.strip()
        else:  # 기간이 하나의 값으로만 되어 있는 경우
            start_date = end_date = full_date.strip()

    # 공연 시간
    match_show_time = re.search(r"공연\s*시간\s*[:：]?\s*([^\n]+)", page_text)
    if match_show_time:
        show_time = match_show_time.group(1).strip()
    else:
        show_time = full_date.strip()

    # 공연 장소
    match_location = re.search(r"공연\s*장소\s*[:：]?\s*([^\n]+)", page_text)
    if match_location:
        location = match_location.group(1).strip()

    # 티켓 가격
    match_price = re.search(r"티켓\s*가격\s*[:：]?\s*([^\n]+)", page_text)
    if match_price:
        price = match_price.group(1).strip()

    # 관람 시간
    match_running_time = re.search(r"관람\s*시간\s*[:：]?\s*([^\n]+)", page_text)
    if match_running_time:
        running_time = match_running_time.group(1).strip()

    # 관람 등급
    match_rating = re.search(r"관람\s*등급\s*[:：]?\s*([^\n]+)", page_text)
    if match_rating:
        rating = match_rating.group(1).strip()


    ################## 포스터 URL, 제목, 예매처 링크 ##################
    try:
        # 포스터 URL
        poster_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "thumb"))
        ).find_element(By.TAG_NAME, "img")
        poster_url = poster_element.get_attribute("src")

        # 공연 제목
        title_element = wait.until(
            EC.presence_of_element_located((By.ID, "noticeTitle"))
        )
        full_title = title_element.get_attribute("textContent").strip()

        # "단독판매" 제거
        if "단독판매" in full_title:
            full_title = full_title.replace("[단독판매]", "").strip()

        if "티켓오픈 안내" in full_title:
            title = full_title.split("티켓오픈 안내")[0].strip()
        elif "\u200b" in full_title:
            title = full_title.split("\u200b")[0].strip()
        else:
            title = full_title  # 분리 기준이 없으면 전체 제목 사용

        # 예매처 링크
        try:
            last_dd = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "th_info"))
            ).find_elements(By.TAG_NAME, "dd")[-1]
            link_element = last_dd.find_element(By.TAG_NAME, "a")
            ticket_link = link_element.get_attribute("href")
        except NoSuchElementException:
            ticket_link = "예매 링크 없음"

    except Exception as e:
        print(f"포스터, 공연 제목, 예매처 링크 로드 실패: {e}")

    ################## 예매일 ##################
   
    # 티켓 오픈일
    open_date_element = driver.find_element(By.ID, "ticketOpenDatetime")
    open_date = open_date_element.text.strip()
    
    # 공지사항 영역의 전체 텍스트 추출
    try:
        announcement_section = driver.find_element(By.CLASS_NAME, "list_view")
        full_text = announcement_section.text.strip()
    except NoSuchElementException:
        print("공지사항 영역을 찾을 수 없습니다.")
        full_text = ""

    # 선예매와 일반 예매 키워드 목록
    pre_open_keywords = ["선예매", "팬클럽 선예매", "멤버십 선예매", "사전 예매", "예매 일정"]
    general_open_keywords = ["일반 예매", "오픈예매", "일반예매"]

    # 정규식: 날짜 및 시간 패턴

    date_time_pattern = r"(\d{4}년\s*\d{1,2}월\s*\d{1,2}일(?:\([^)]+\))?)\s*([오전|오후]*\s*\d{1,2}시(?:\s*\d{1,2}분)?(?:\s*\d{1,2}초)?|\d{1,2}:\d{2}(?::\d{2})?)"

    # 텍스트를 줄 단위로 나눔
    lines = full_text.split("\n")

    # 키워드 기반 탐색
    for line in lines:
        line = line.strip()

        # 휠체어석 예매를 무시
        if "휠체어석" in line:
            continue
        
        if "팬클럽 선예매 인증 기간" in line:
            continue

        if "멤버십 선예매 인증 기간" in line:
            continue

        # 선예매 키워드 탐색
        if any(keyword in line for keyword in pre_open_keywords):
            if pre_open_date is None:  # 이미 값이 설정된 경우 덮어쓰지 않음
                match = re.search(date_time_pattern, line)
                if match:
                    date, time = match.groups()  # 날짜와 시간을 분리
                    pre_open_date = f"{date} {time}".strip()

        def normalize_date(raw_date):
            """날짜를 xxxx.xx.xx 형식으로 정규화"""
            return re.sub(r"[^0-9.]", "", raw_date)
        
        # 일반 예매 키워드 탐색
        if any(keyword in line for keyword in general_open_keywords):
            match = re.search(date_time_pattern, line)
            if match:
                date, time = match.groups()  # 날짜와 시간을 분리
                detected_date = f"{date} {time}".strip()

                # 기존 open_date와 비교 (정규화된 형식으로)
                normalized_open_date = normalize_date(open_date) if open_date else None
                normalized_detected_date = normalize_date(detected_date)

                # 날짜가 다르면 open_date 갱신
                if normalized_open_date != normalized_detected_date:
                    open_date = detected_date

    ################## 데이터 출력 ##################
    print(f"포스터 URL: {poster_url}")
    print(f"공연 제목: {title}")
    print(f"예매처 링크: {ticket_link}")
    print(f"공연 시작일: {start_date}")
    print(f"공연 종료일: {end_date}")
    
    print(f"공연 시간: {show_time}")
    print(f"공연 장소: {location}")
    print(f"티켓 가격: {price}")
    print(f"관람 시간: {running_time}")
    print(f"관람 등급: {rating}")
    print(f"선예매 날짜: {pre_open_date}")
    print(f"일반 예매 날짜: {open_date}")

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    driver.quit()
    print("추출 완료")
