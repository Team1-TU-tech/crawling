import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from valid_links import * 

driver = initialize_driver()

# 날짜 xxxx.xx.xx 형식 정규화
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

# 날짜 및 시간 xxxx.xx.xx (시분 선택) xx:xx 형식 정규화
def normalize_datetime(raw_text):
    # 범위(~) 처리
    if "~" in raw_text or "-" in raw_text:
        match = re.search(r"(.+?)\s*~", raw_text)
        if match:
            pre_range_text = match.group(1).strip()
        else:
            pre_range_text = raw_text.strip()
    else:
        pre_range_text = raw_text.strip()

    # 전처리: 숫자가 아닌 문자 제거 및 KST, 괄호 제거
    pre_range_text = re.sub(r"^[^\d]*", "", pre_range_text).strip()  # 숫자 외 문자 제거
    pre_range_text = re.sub(r"\(KST\)", "", pre_range_text).strip()  # KST 제거
    pre_range_text = re.sub(r"\([^)]*\)", "", pre_range_text).strip()  # 괄호 안 텍스트 제거
    pre_range_text = pre_range_text.replace("년 ", ".").replace("월 ", ".").replace("일", "").strip()

    # 날짜 및 시간 패턴
    date_time_pattern = r"(\d{4}[.\-]\d{1,2}[.\-]\d{1,2})\s*(오전|오후)?\s*(\d{1,2}:\d{2}(?::\d{2})?|\d{1,2}시(?:\s*\d{1,2}분)?)"
    
    match = re.search(date_time_pattern, pre_range_text)
    if match:
        raw_date, am_pm, time = match.groups()
        
        # 날짜 분해
        year, month, day = map(int, raw_date.split("."))
        hour, minute = 0, 0
        
        # 시간 처리
        if time:
            time_match = re.search(r"(\d{1,2}):(\d{2})", time)
            if time_match:
                hour, minute = map(int, time_match.groups())
            else:
                hour = int(re.search(r"(\d{1,2})시", time).group(1))
                minute_match = re.search(r"(\d{1,2})분", time)
                minute = int(minute_match.group(1)) if minute_match else 0
        
        # 오전/오후 처리
        if am_pm == "오후" and hour < 12:
            hour += 12
        elif am_pm == "오전" and hour == 12:
            hour = 0

        # 날짜 및 시간 반환
        return f"{year:04d}.{month:02d}.{day:02d} {hour:02d}:{minute:02d}"
    else:
        print(f"날짜/시간 매칭 실패")  

    return None

# 공연 설명 추출
def extract_description(full_text):
    try:
        start_keywords = ["공연내용", "공연 내용", "[공연내용]", "[공연 내용]", "공연소개", "공연 소개", "[공연소개]", "[공연 소개]", "◈공연소개"]
        end_keywords = ["기획사정보", "캐스팅", "기획사 정보", "공지사항"]
        description = []  # 공연 설명을 저장할 리스트
        is_description_section = False  # 설명 섹션 여부 플래그
        empty_line_count = 0  # 빈 줄 카운트

        # 텍스트를 줄 단위로 분리
        lines = full_text.split("\n")
        
        for line in lines:
            line = line.strip()  # 줄 앞뒤 공백 제거

            # 빈 줄 카운트 처리
            if not line:
                empty_line_count += 1
            else:
                empty_line_count = 0  # 내용이 있으면 빈 줄 카운트 초기화

            # 2줄 이상의 빈 줄이 연속되면 설명 종료
            if empty_line_count >= 2 and is_description_section:
                break

            # 설명 섹션 시작 조건 
            if not is_description_section and any(keyword in line for keyword in start_keywords):
                is_description_section = True
                continue 

            # 설명 섹션 종료 조건
            if is_description_section and any(keyword in line for keyword in end_keywords):
                break

            # 설명 섹션에 해당하는 내용 추가
            if is_description_section and line:
                description.append(line)

        # 설명이 있으면 반환, 없으면 기본값 반환
        return "\n".join(description).strip() if description else "공연설명 없음"

    except Exception as e:
        print(f"공연설명 추출 중 오류 발생: {e}")
        return "공연설명 추출 실패"
    

# 본문 - 공연 정보 추출 (공연 시간, 장소, 가격, 관람 시간)
def extract_performance_info(page_text):

    match_date = re.search(r"공연\s*(일시|기간)\s*[:：]?\s*([^\n]+)", page_text)
    start_date, end_date = None, None

    if match_date:
        full_date = match_date.group(2).strip()
        if " ~ " in full_date:
            start_date, end_date = full_date.split(" ~ ")
        elif " - " in full_date:
            start_date, end_date = full_date.split(" - ")
        else:
            start_date = end_date = full_date.strip()

        start_date = normalize_date(start_date.strip()) if start_date else None
        end_date = normalize_date(end_date.strip()) if end_date else None
  
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

    return start_date, end_date, show_time, location, price, running_time, rating

# 헤더 - 공연 정보 추출 (포스터 URL, 제목, 예매처 링크, 카테고리)
def extract_header(wait):
    
    # 포스터 URL, 제목 
    try:
        poster_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "thumb"))
        ).find_element(By.TAG_NAME, "img")
        poster_url = poster_element.get_attribute("src")

        title_element = wait.until(
            EC.presence_of_element_located((By.ID, "noticeTitle"))
        )
        full_title = title_element.get_attribute("textContent").strip()

        # 단독판매여부 체크
        exclusive = 1 if "단독판매" in full_title else 0

        full_title = full_title.replace("\u200b", "").strip()
        
        # 필요없는 정보빼고 타이틀 추출 
        if "단독판매" in full_title:
            full_title = full_title.replace("[단독판매]", "").strip()

        if "티켓오픈 안내" in full_title:
            title = full_title.split("티켓오픈 안내")[0].strip()
        elif "\u200b" in full_title:
            title = full_title.split("\u200b")[0].strip()
        else:
            title = full_title.strip()

        # 제목 키워드 기준으로 카테고리 분류
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

        return poster_url, title, category, ticket_link, exclusive
    
    except Exception as e:
        print(f"포스터, 공연 제목, 예매처 링크 로드 실패: {e}")
        return None, None, None, None, 0


def extract_open_date(driver, page_text):

    open_date = None
    pre_open_date = None

    # 예매일 추출
    try:
        open_date_element = driver.find_element(By.ID, "ticketOpenDatetime")
        open_date = open_date_element.text.strip()
        
    except NoSuchElementException:
        open_date = None    
        print("예매일 정보를 찾을 수 없습니다.") 
    
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
                    pre_open_date = normalize_datetime(line)
                
        if any(keyword in line for keyword in general_open_keywords):
            match = re.search(date_time_pattern, line)
            if match:
                detected_date = normalize_datetime(line)

                if open_date:
                    normalized_open_date = normalize_datetime(open_date)
                else:
                    normalized_open_date = None

                if normalized_open_date and normalize_date(open_date.split(" ")[0]) == normalize_date(detected_date.split(" ")[0]):
                    open_date = detected_date
                else:
                    open_date = detected_date

        if open_date and not any(keyword in page_text for keyword in general_open_keywords):
            open_date = normalize_datetime(open_date)
        
    return open_date, pre_open_date
    

def crawl_data(driver, csoonID):
    csoon_url = f"https://www.ticketlink.co.kr/help/notice/{csoonID}"
    driver.get(csoon_url)
    print(f"페이지 로드 완료: {driver.current_url}")
    wait = WebDriverWait(driver, 10)

    # 데이터 초기화
    data = {
        'poster_url': None, 'title': None, 'ticket_link': None, 'start_date': None, 'end_date': None,
        'show_time': None, 'location': None, 'price': None, 'running_time': None, 'rating': None,
        'open_date': None, 'pre_open_date': None, 'exclusive': 0, 'category': None, 'performance_description': None
    }

    try:
        # 전체 텍스트 추출
        page_text = driver.find_element(By.TAG_NAME, "body").text

        ################## 본문 공연 정보 추출 ##################
        start_date, end_date, show_time, location, price, running_time, rating = extract_performance_info(page_text)

        ################## 헤더 공연 정보 추출 ##################
        poster_url, title, category, ticket_link, exclusive = extract_header(wait)

        ################## 예매일 추출 ##################
        open_date, pre_open_date = extract_open_date(driver, page_text)

        ################## 공연 설명 추출 ##################
        announcement_section = driver.find_element(By.CLASS_NAME, "list_view")
        full_text = announcement_section.text.strip()
        performance_description = extract_description(full_text)

        # 데이터 업데이트
        data.update({
            'poster_url': poster_url, 'title': title, 'ticket_link': ticket_link,
            'start_date': start_date, 'end_date': end_date, 'show_time': show_time,
            'location': location, 'price': price, 'running_time': running_time, 'rating': rating,
            'open_date': open_date, 'pre_open_date': pre_open_date, 'exclusive': exclusive, 'category': category,
            'performance_description': performance_description
        })

        print(data)

    except Exception as e:
        print(f"공연 정보 추출 중 오류 발생: {e}")
    
    return data

crawl_data(driver)