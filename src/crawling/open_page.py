from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime

# 테스트할 웹사이트 URL
#test_url = "https://www.ticketlink.co.kr/help/notice/57930"  # 에스파
#test_url = "https://www.ticketlink.co.kr/help/notice/59062"  # 남주
#test_url = "https://www.ticketlink.co.kr/help/notice/59142"  # 베리베리

#test_url = "https://www.ticketlink.co.kr/help/notice/60826" # 호두까기 인형
#test_url = "https://www.ticketlink.co.kr/help/notice/45261"
#test_url = "https://www.ticketlink.co.kr/help/notice/60831"

test_url = "https://www.ticketlink.co.kr/help/notice/60844"
#test_url = "https://www.ticketlink.co.kr/help/notice/60856"

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 필요 시 헤드리스 모드 활성화
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

def normalize_date(raw_date, base_year=None):
    # 현재 연도 기본값으로 설정
    if base_year is None:
        base_year = datetime.now().year

    # 숫자만 추출
    number = re.sub(r"[^0-9]", "", raw_date)
    
    # 연도, 월, 일이 모두 있는 경우
    if len(number) == 8:
        return f"{number[:4]}.{number[4:6]}.{number[6:]}"
    
    # 연도가 없는 경우 현재 연도(base_year) 추가
    match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", raw_date)
    if match:
        month, day = match.groups()
        return f"{base_year}.{int(month):02d}.{int(day):02d}"
    
    # 월, 일이 없는 경우 숫자만 반환
    return None

def normalize_datetime_range(raw_text, base_year=None):
    # ~ 앞의 텍스트 추출
    if "~" in raw_text:
        match = re.search(r"(.+?)\s*~", raw_text)
        if match:
            pre_range_text = match.group(1).strip()
        else:
            pre_range_text = raw_text.strip()  # 매칭 실패 시 전체 텍스트 사용
    else:
        pre_range_text = raw_text.strip()  # ~ 기호가 없는 경우 전체 텍스트 사용

    # 불필요한 접두어, 요일, 및 (KST) 제거
    pre_range_text = re.sub(r"^[^\d]*", "", pre_range_text).strip()  # 접두어 제거
    pre_range_text = re.sub(r"\(KST\)", "", pre_range_text).strip()  # (KST) 제거
    pre_range_text = re.sub(r"\([^)]*\)", "", pre_range_text).strip()  # 요일 제거
    pre_range_text = pre_range_text.replace("년 ", ".").replace("월 ", ".").replace("일", "").strip()  # 한국어 날짜 형식 변환

def normalize_datetime_range(raw_text, base_year=None):

    # ~ 앞의 텍스트 추출
    if "~" in raw_text:
        match = re.search(r"(.+?)\s*~", raw_text)
        if match:
            pre_range_text = match.group(1).strip()
        else:
            pre_range_text = raw_text.strip()  # 매칭 실패 시 전체 텍스트 사용
    else:
        pre_range_text = raw_text.strip()  # ~ 기호가 없는 경우 전체 텍스트 사용
        
    # 불필요한 접두어, 요일, 및 (KST) 제거
    pre_range_text = re.sub(r"^[^\d]*", "", pre_range_text).strip()  # 접두어 제거
    pre_range_text = re.sub(r"\(KST\)", "", pre_range_text).strip()  # (KST) 제거
    pre_range_text = re.sub(r"\([^)]*\)", "", pre_range_text).strip()  # 요일 제거
    pre_range_text = pre_range_text.replace("년 ", ".").replace("월 ", ".").replace("일", "").strip()  # 한국어 날짜 형식 변환

    # 날짜와 시간 정규식
    date_time_pattern = r"(\d{4}[.\-]\d{1,2}[.\-]\d{1,2})\s*(오전|오후)?\s*(\d{1,2}:\d{2}(?::\d{2})?|\d{1,2}시(?:\s*\d{1,2}분)?)"
    match = re.search(date_time_pattern, pre_range_text)
    if match:
        raw_date, am_pm, time = match.groups()

        # 날짜 정규화
        year, month, day = map(int, raw_date.split("."))

        # 시간 정규화
        time_match = re.search(r"(\d{1,2}):(\d{2})", time)  # HH:MM
        if time_match:
            hour, minute = time_match.groups()
            hour = int(hour)
            minute = int(minute)
        else:
            hour = int(re.search(r"(\d{1,2})시", time).group(1))
            minute_match = re.search(r"(\d{1,2})분", time)
            minute = int(minute_match.group(1)) if minute_match else 0


        # 오전/오후 처리
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
    performance_description = None

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

        normalized_start_date = normalize_date(start_date) if start_date else None
        normalized_end_date = normalize_date(end_date) if end_date else None


    # 공연 시간
    match_show_time = re.search(r"공연\s*시간\s*[:：]?\s*([^\n]+)", page_text)
    if match_show_time:
        show_time = match_show_time.group(1).strip()
    else:
        show_time = full_date.strip()

    # 공연 장소
    match_location = re.search(r"공연\s*장소\s*[:：\-]?\s*([^\n]+)", page_text)
    if match_location:
        location = match_location.group(1).strip()

    # 티켓 가격
    match_price = re.search(r"티켓\s*가격\s*[:：\-]?\s*([^\n]+)", page_text)
    if match_price:
        price = match_price.group(1).strip()
    
    # 관람 시간
    match_running_time = re.search(r"관람\s*시간\s*[:：\-]?\s*([^\n]+)", page_text)
    if match_running_time:
        running_time = match_running_time.group(1).strip()

    # 관람 등급
    match_rating = re.search(r"관람\s*등급\s*[:：\-]?\s*([^\n]+)", page_text)
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

        # "단독판매" 여부 확인 및 제거
        exclusive = 0  # 단독판매 아닌 기본 값
        if "단독판매" in full_title:
            exclusive = 1  # 단독판매인 경우 1로 설정
            full_title = full_title.replace("[단독판매]", "").strip()

        # "단독판매" 제거
        if "단독판매" in full_title:
            full_title = full_title.replace("[단독판매]", "").strip()

        # "티켓오픈 안내" 제거
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
    general_open_keywords = ["일반 예매", "오픈예매", "일반예매", "예매 일정"]

    # 정규식: 날짜 및 시간 패턴

    #date_time_pattern = r"(\d{4}년\s*\d{1,2}월\s*\d{1,2}일(?:\([^)]+\))?)\s*([오전|오후]*\s*\d{1,2}시(?:\s*\d{1,2}분)?(?:\s*\d{1,2}초)?|\d{1,2}:\d{2}(?::\d{2})?)"
    #date_time_pattern = r"(\d{4}년\s*\d{1,2}월\s*\d{1,2}일(?:\([^)]+\))?)\s*([오전|오후]*\s*\d{1,2}시(?:\s*\d{1,2}분)?(?:\s*\d{1,2}초)?|\d{1,2}:\d{2})"
    date_time_pattern = r"(\d{4}년\s*\d{1,2}월\s*\d{1,2}일(?:\([^)]*\))?)\s*(오전|오후)?\s*(\d{1,2}:\d{2}(?::\d{2})?)?"

    # 텍스트를 줄 단위로 나눔
    lines = full_text.split("\n")

    # 키워드 기반 탐색
    for line in lines:
        line = line.strip()

        # 해당 키워드들 무시
        
        if "팬클럽 선예매 인증 기간" in line:
            continue

        if "멤버십 선예매 인증 기간" in line:
            continue

        # 선예매 키워드 탐색
        if any(keyword in line for keyword in pre_open_keywords):
            if pre_open_date is None:  # 이미 값이 설정된 경우 덮어쓰지 않음
                match = re.search(date_time_pattern, line)
                if match:
                    pre_open_date = normalize_datetime_range(line)  # 날짜와 시간을 정규화
                
        # 일반예매 키워드 탐색
        if any(keyword in line for keyword in general_open_keywords):
            match = re.search(date_time_pattern, line)
            if match:
                detected_date = normalize_datetime_range(line)  # 날짜와 시간을 정규화

                # 기존 open_date 정규화
                if open_date:
                    normalized_open_date = normalize_datetime_range(open_date)
                else:
                    normalized_open_date = None

                # 날짜가 같으면 티켓 오픈일 갱신 (시간 포함 정규화)
                if normalized_open_date and normalize_date(open_date.split(" ")[0]) == normalize_date(detected_date.split(" ")[0]):
                    open_date = detected_date  # 탐색된 값을 시간까지 포함하여 갱신
                else:  # 날짜가 다르면 탐색된 값을 사용
                    open_date = detected_date


        # 본문에 일반 예매 키워드가 없을 경우 open_date 정규화
        if open_date and not any(keyword in page_text for keyword in general_open_keywords):
            open_date = normalize_datetime_range(open_date)

################################공연설명##########################################
# ##1. 볼드

# # 공연설명 추출 - 볼드 태그 기준 종료
#     def extract_performance_description_bold(full_text):
#         try:
#             start_keywords = [
#                 "공연내용", "공연 내용", "[공연내용]", "[공연 내용]",
#                 "공연소개", "공연 소개", "[공연소개]", "[공연 소개]",
#                 "◈공연소개"
#             ]
#             bold_end_pattern = r"<b>"  # 볼드 태그 기준 종료
#             description = []
#             is_description_section = False
#             lines = full_text.split("\n")

#             for line in lines:
#                 line = line.strip()
#                 if not is_description_section and any(keyword in line for keyword in start_keywords):
#                     is_description_section = True
#                     continue
#                 if is_description_section and re.search(bold_end_pattern, line):
#                     break
#                 if is_description_section:
#                     description.append(line)

#             return "\n".join(description).strip() if description else "공연설명 없음"
#         except Exception as e:
#             print(f"공연설명 추출 중 오류 발생 (볼드 기준): {e}")
#             return "공연설명 추출 실패"

    # bold_based_description = extract_performance_description_bold(full_text)
    # print(f"공연 소개: {bold_based_description}")
    
## 2. 줄바꿈
# 공연설명 추출 - 줄바꿈 2번 이상 기준 종료
# 공연설명 추출 - 줄바꿈 2번 이상 또는 종료 키워드 기준 종료
    def extract_performance_description_with_keywords(full_text):
        try:
            start_keywords = [
                "공연내용", "공연 내용", "[공연내용]", "[공연 내용]",
                "공연소개", "공연 소개", "[공연소개]", "[공연 소개]",
                "◈공연소개"
            ]
            end_keywords = ["기획사정보", "캐스팅", "기획사 정보", "공지사항"]  # 종료 키워드

            description = []
            is_description_section = False
            empty_line_count = 0  # 연속 빈 줄 감지용
            lines = full_text.split("\n")

            for line in lines:
                line = line.strip()  # 양쪽 공백 제거

                # 빈 줄 여부 확인
                if not line:
                    empty_line_count += 1
                else:
                    empty_line_count = 0  # 빈 줄이 아니면 카운트 초기화

                # 줄바꿈 2번 이상 감지 시 종료
                if empty_line_count >= 2 and is_description_section:
                    break

                # 종료 키워드 탐지 시 종료
                if is_description_section and any(keyword in line for keyword in end_keywords):
                    break

                # 시작 키워드 탐지
                if not is_description_section and any(keyword in line for keyword in start_keywords):
                    is_description_section = True
                    continue  # 키워드가 포함된 줄은 제외하고 다음 줄부터 읽음

                # 공연설명 추가
                if is_description_section and line:  # 빈 줄은 저장하지 않음
                    description.append(line)

            # 공연설명 결과 반환
            return "\n".join(description).strip() if description else "공연설명 없음"
        except Exception as e:
            print(f"공연설명 추출 중 오류 발생: {e}")
            return "공연설명 추출 실패"


    # bold_based_description = extract_performance_description_bold(full_text)
    linebreak_based_description = extract_performance_description_with_keywords(full_text) 
    
    ################## 데이터 출력 ##################
    
    print(f"공연 소개: {linebreak_based_description}")

    print(f"포스터 URL: {poster_url}")
    print(f"공연 제목: {title}")
    print(f"예매처 링크: {ticket_link}")
    print(f"공연 시작일: {normalized_start_date}")
    print(f"공연 종료일: {normalized_end_date}")
    
    print(f"공연 시간: {show_time}")
    print(f"공연 장소: {location}")
    print(f"티켓 가격: {price}")
    print(f"관람 시간: {running_time}")
    print(f"관람 등급: {rating}")

    print(f"선예매 날짜: {pre_open_date}")
    print(f"일반 예매 날짜: {open_date}")
    print(f"단독판매 여부: {exclusive}")

except Exception as e:
    print(f"오류 발생: {e}")
    exclusive = None

finally:
    driver.quit()
    print("추출 완료")