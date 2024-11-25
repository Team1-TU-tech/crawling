from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime
from valid_links import valid_links  # valid_links.py에서 valid_links 리스트 가져오기
import os

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# 텍스트 파일 저장 디렉토리 설정, 테스트용
txt_save_directory = os.path.join(os.getcwd(), "txt_files")
os.makedirs(txt_save_directory, exist_ok=True)  # 디렉토리가 없으면 생성

def normalize_date(raw_date, base_year=None):
    if base_year is None:
        base_year = datetime.now().year

    number = re.sub(r"[^0-9]", "", raw_date)
    if len(number) == 8:
        return f"{number[:4]}.{number[4:6]}.{number[6:]}"

    match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", raw_date)
    if match:
        month, day = match.groups()
        return f"{base_year}.{int(month):02d}.{int(day):02d}"
    
    return None

def normalize_datetime_range(raw_text, base_year=None):
    if "~" in raw_text or "-" in raw_text:
        match = re.search(r"(.+?)\s*~", raw_text)
        if match:
            pre_range_text = match.group(1).strip()
        else:
            pre_range_text = raw_text.strip()
    else:
        pre_range_text = raw_text.strip()

    pre_range_text = re.sub(r"^[^\d]*", "", pre_range_text).strip()
    pre_range_text = re.sub(r"\(KST\)", "", pre_range_text).strip()
    pre_range_text = re.sub(r"\([^)]*\)", "", pre_range_text).strip()
    pre_range_text = pre_range_text.replace("년 ", ".").replace("월 ", ".").replace("일", "").strip()

    date_time_pattern = r"(\d{4}[.\-]\d{1,2}[.\-]\d{1,2})\s*(오전|오후)?\s*(\d{1,2}:\d{2}(?::\d{2})?|\d{1,2}시(?:\s*\d{1,2}분)?)"
    match = re.search(date_time_pattern, pre_range_text)
    if match:
        raw_date, am_pm, time = match.groups()

        year, month, day = map(int, raw_date.split("."))

        time_match = re.search(r"(\d{1,2}):(\d{2})", time)
        if time_match:
            hour, minute = time_match.groups()
            hour = int(hour)
            minute = int(minute)
        else:
            hour = int(re.search(r"(\d{1,2})시", time).group(1))
            minute_match = re.search(r"(\d{1,2})분", time)
            minute = int(minute_match.group(1)) if minute_match else 0

        if am_pm == "오후" and hour < 12:
            hour += 12
        elif am_pm == "오전" and hour == 12:
            hour = 0

        normalized_datetime = f"{year:04d}.{month:02d}.{day:02d} {hour:02d}:{minute:02d}"
        return normalized_datetime
    else:
        print(f"날짜/시간 매칭 실패")  

    return None


try:

    # 각 csoonID에 대해 정보 크롤링
    for link_data in valid_links:
        csoonID = link_data["csoonID"]  # valid_links에서 csoonID 가져오기
        test_url = f"https://www.ticketlink.co.kr/help/notice/{csoonID}"
        driver.get(test_url)

        wait = WebDriverWait(driver, 10)

    ################## 데이터 초기화 ##################
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
    performance_description = None
    category = None
    exclusive = 0
    
    ################## 전체 텍스트 추출 ##################
    page_text = driver.find_element(By.TAG_NAME, "body").text

    ################## 공연 정보 추출 ##################
    match_date = re.search(r"공연\s*(일시|기간)\s*[:：]?\s*([^\n]+)", page_text)

    if match_date:
        full_date = match_date.group(2).strip()
        if " ~ " in full_date:
            start_date, end_date = full_date.split(" ~ ")
        elif " - " in full_date:
            start_date, end_date = full_date.split(" - ")
        else:
            start_date = end_date = full_date.strip()

        start_date = start_date.strip()
        end_date = end_date.strip()

        start_date = normalize_date(start_date) if start_date else None
        end_date = normalize_date(end_date) if end_date else None

    match_show_time = re.search(r"공연\s*시간\s*[:：]?\s*([^\n]+)", page_text)
    show_time = match_show_time.group(1).strip() if match_show_time else full_date.strip()

    match_location = re.search(r"공연\s*장소\s*[:：\-]?\s*([^\n]+)", page_text)
    location = match_location.group(1).strip() if match_location else None

    match_price = re.search(r"티켓\s*가격\s*[:：\-]?\s*([^\n]+)", page_text)
    price = match_price.group(1).strip() if match_price else None
    
    match_running_time = re.search(r"관람\s*시간\s*[:：\-]?\s*([^\n]+)", page_text)
    running_time = match_running_time.group(1).strip() if match_running_time else None

    match_rating = re.search(r"관람\s*등급\s*[:：\-]?\s*([^\n]+)", page_text)
    rating = match_rating.group(1).strip() if match_rating else None

    ################## 포스터 URL, 제목, 예매처 링크 ##################
    try:
        poster_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "thumb"))
        ).find_element(By.TAG_NAME, "img")
        poster_url = poster_element.get_attribute("src")

        title_element = wait.until(
            EC.presence_of_element_located((By.ID, "noticeTitle"))
        )
        full_title = title_element.get_attribute("textContent").strip()

        if "단독판매" in full_title:
            exclusive = 1
            full_title = full_title.replace("[단독판매]", "").strip()

        if "티켓오픈 안내" in full_title:
            title = full_title.split("티켓오픈 안내")[0].strip()
        elif "\u200b" in full_title:
            title = full_title.split("\u200b")[0].strip()
        else:
            title = full_title

        # 제목 키워드 기준으로 카테고리 간단히 분류
        if "뮤지컬" in title or "연극" in title:
            category = "뮤지컬/연극"
        elif "콘서트" in title:
            category = "콘서트"
        else:
            category = "전시/행사"

        try:
            last_dd = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "th_info"))
            ).find_elements(By.TAG_NAME, "dd")[-1]
            link_element = last_dd.find_element(By.TAG_NAME, "a")
            ticket_link = link_element.get_attribute("href")
        except NoSuchElementException:
            ticket_link = "예매 링크 없음"

    except Exception as e:
        poster_url = None
        title = None
        ticket_link = None
        exclusive = 0
        print(f"포스터, 공연 제목, 예매서 링크 로드 실패: {e}")

    ################## 예매일 ##################
    try:
        open_date_element = driver.find_element(By.ID, "ticketOpenDatetime")
        open_date = open_date_element.text.strip()
    except NoSuchElementException:
        open_date = None

    try:
        announcement_section = driver.find_element(By.CLASS_NAME, "list_view")
        full_text = announcement_section.text.strip()
    except NoSuchElementException:
        print("공지사항 영역을 찾을 수 없습니다.")
        full_text = ""

    pre_open_keywords = ["선예매", "팬클럽 선예매", "멤버십 선예매", "사전 예매", "예매 일정"]
    general_open_keywords = ["일반 예매", "오픈예매", "일반예매", "예매 일정"]

    date_time_pattern = r"(\d{4}년\s*\d{1,2}월\s*\d{1,2}일(?:\([^)]*\))?)\s*(오전|오후)?\s*(\d{1,2}:\d{2}(?::\d{2})?)?"

    lines = full_text.split("\n")

    for line in lines:
        line = line.strip()
        if "팬클럽 선예매 인증 기간" in line or "멤버십 선예매 인증 기간" in line:
            continue

        if any(keyword in line for keyword in pre_open_keywords):
            if pre_open_date is None:
                match = re.search(date_time_pattern, line)
                if match:
                    pre_open_date = normalize_datetime_range(line)
                
        if any(keyword in line for keyword in general_open_keywords):
            match = re.search(date_time_pattern, line)
            if match:
                detected_date = normalize_datetime_range(line)

                if open_date:
                    normalized_open_date = normalize_datetime_range(open_date)
                else:
                    normalized_open_date = None

                if normalized_open_date and normalize_date(open_date.split(" ")[0]) == normalize_date(detected_date.split(" ")[0]):
                    open_date = detected_date
                else:
                    open_date = detected_date

        if open_date and not any(keyword in page_text for keyword in general_open_keywords):
            open_date = normalize_datetime_range(open_date)

    ################################공연설명##########################################

    def description(full_text):
        try:
            start_keywords = [
                "공연내용", "공연 내용", "[공연내용]", "[공연 내용]",
                "공연소개", "공연 소개", "[공연소개]", "[공연 소개]",
                "◈공연소개"
            ]
            end_keywords = ["기획사정보", "캐스팅", "기획사 정보", "공지사항"]

            description = []
            is_description_section = False
            empty_line_count = 0
            lines = full_text.split("\n")

            for line in lines:
                line = line.strip()

                if not line:
                    empty_line_count += 1
                else:
                    empty_line_count = 0

                if empty_line_count >= 2 and is_description_section:
                    break

                if is_description_section and any(keyword in line for keyword in end_keywords):
                    break

                if not is_description_section and any(keyword in line for keyword in start_keywords):
                    is_description_section = True
                    continue

                if is_description_section and line:
                    description.append(line)

            return "\n".join(description).strip() if description else "공연설명 없음"
        except Exception as e:
            print(f"공연설명 추출 중 오류 발생: {e}")
            return "공연설명 추출 실패"

    performance_description = description(full_text)
    
    ################## 데이터 출력 ##################
    open_page = {
        'poster_url': poster_url,
        'title': title,
        'ticket_link': ticket_link,
        'start_date': start_date,
        'end_date': end_date,
        'show_time': show_time,
        'location': location,
        'price': price,
        'running_time': running_time,
        'rating': rating,
        'open_date': open_date,
        'pre_open_date': pre_open_date,
        'exclusive': exclusive,
        'category': category,
        'performance_description': performance_description
    }
    
    # csoonID를 파일 이름으로 저장
    txt_filename = os.path.join(txt_save_directory, f"{csoonID}.txt")
    with open(txt_filename, mode='w', encoding='utf-8') as txt_file:
        for key, value in open_page.items():
            txt_file.write(f"{key}: {value}\n")
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    driver.quit()
    print("추출 완료")
