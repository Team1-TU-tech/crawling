import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from detail_page import *


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
webdriver.Chrome(options=options)

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
        end_keywords = ["기획사정보", "캐스팅", "기획사 정보", "공지사항", "출연자 정보", "출연자", "출연자정보"]
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
        return "\n".join(description).strip() if description else None

    except Exception as e:
        print(f"공연설명 추출 중 오류 발생: {e}")
        return "공연설명 추출 실패"
    

# 본문 - 공연 정보 추출 (공연 시간, 장소, 가격, 관람 시간)
def extract_performance_info(page_text):
    # 기본값 초기화
    start_date, end_date = None, None
    show_time = None
    location = None
    price = None
    running_time = None
    rating = None
    full_date = None

    try:
        # 공연 일시 또는 기간 추출
        match_date = re.search(r"공연\s*(일시|기간)\s*[:：]?\s*([^\n]+)", page_text)
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

    except Exception as e:
        print(f"공연 일시 추출 중 오류: {e}")

    try:
        # 공연 시간 추출
        match_show_time = re.search(r"공연\s*시간\s*[:：]?\s*([^\n]+)", page_text)
        show_time = match_show_time.group(1).strip() if match_show_time else None

    except Exception as e:
        print(f"공연 시간 추출 중 오류: {e}")

    try:
        # 공연 장소 추출
        match_location = re.search(r"공연\s*장소\s*[:：\-]?\s*([^\n]+)", page_text)
        location = match_location.group(1).strip() if match_location else None

    except Exception as e:
        print(f"공연 장소 추출 중 오류: {e}")

    try:
        # 티켓 가격 추출
        match_price = re.search(r"티켓\s*가격\s*[:：\-]?\s*([^\n]+)", page_text)
        price = match_price.group(1).strip() if match_price else None

    except Exception as e:
        print(f"티켓 가격 추출 중 오류: {e}")

    try:
        # 관람 시간 추출
        match_running_time = re.search(r"관람\s*시간\s*[:：\-]?\s*([^\n]+)", page_text)
        running_time = match_running_time.group(1).strip() if match_running_time else None

    except Exception as e:
        print(f"관람 시간 추출 중 오류: {e}")

    try:
        # 관람 등급 추출
        match_rating = re.search(r"관람\s*등급\s*[:：\-]?\s*([^\n]+)", page_text)
        rating = match_rating.group(1).strip() if match_rating else None

    except Exception as e:
        print(f"관람 등급 추출 중 오류: {e}")

    # 추출된 정보 반환
    return start_date, end_date, show_time, location, price, running_time, rating

# 헤더 - 공연 정보 추출 (포스터 URL, 제목, 예매처 링크, 카테고리)
def extract_header(wait):
    poster_url = None
    title = None
    category = None
    ticket_link = None
    exclusive = 0

    try:
        # 포스터 URL 추출
        try:
            poster_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "thumb"))
            ).find_element(By.TAG_NAME, "img")
            poster_url = poster_element.get_attribute("src")
        except NoSuchElementException:
            print("포스터 URL을 찾을 수 없습니다. 포스터는 None으로 설정됩니다.")

        # 제목 추출
        try:
            title_element = None  # 초기화
            full_title = None     # 초기화

            try:
                # 우선 ID로 제목 찾기
                title_element = wait.until(
                    EC.presence_of_element_located((By.ID, "noticeTitle"))
                )
                print("Title found using ID 'noticeTitle'")
            except TimeoutException:
                
                # 없을 경우 XPath로 list_view 내부의 마지막 class='title' 찾기
                title_elements = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//dl[@class='list_view']//dd[@class='title']"))
                )
                if title_elements:
                    title_element = title_elements[-1]  # 마지막 요소 선택
                    print("Title found using XPath 'list_view' and class='title'")
                else:
                    print("No title elements found.")
                    raise Exception("No title elements found in list_view.")

            # 제목 텍스트 추출
            full_title = title_element.get_attribute("textContent").strip() if title_element else None

            # 단독판매 여부 체크
            exclusive = 1 if full_title and "단독판매" in full_title else 0

            # 불필요한 문자 제거
            full_title = full_title.replace("\u200b", "").strip() if full_title else ""
            if "단독판매" in full_title:
                full_title = full_title.replace("[단독판매]", "").strip()

            # 제목 전처리
            if "티켓오픈 안내" in full_title:
                title = full_title.split("티켓오픈 안내")[0].strip()
            elif "예매오픈" in full_title:
                title = full_title.split("예매오픈")[0].strip()
            elif "\u200b" in full_title:
                title = full_title.split("\u200b")[0].strip()
            else:
                title = full_title.strip()

            print(f"Extracted Title: {title}, Exclusive: {exclusive}")

        except Exception as e:
            print(f"타이틀을 찾을 수 없습니다: {e}")

        # 타이틀과 exclusive 둘 다 없으면 건너뛰기 (단, poster_url이 있으면 반환)
        if not title and not exclusive:
            if poster_url:
                print("타이틀과 exclusive는 없지만 포스터 URL이 있어 데이터를 반환합니다.")
                return poster_url, None, None, None, 0
            else:
                print("타이틀, exclusive, 포스터 URL 모두 없습니다. 해당 항목을 건너뜁니다.")
                return None, None, None, None, 0
            
        # 제목 키워드 기준으로 카테고리 분류
        if "뮤지컬" in title or "연극" in title:
            category = "뮤지컬/연극"
        elif "콘서트" in title:
            category = "콘서트"
        else:
            category = "전시/행사"

        # 예매 링크 추출
        try:
            last_dd = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "th_info"))
            ).find_elements(By.TAG_NAME, "dd")[-1]
            link_element = last_dd.find_element(By.TAG_NAME, "a")
            ticket_link = link_element.get_attribute("href")
        except NoSuchElementException:
            print("예매 링크를 찾을 수 없습니다. 예매 링크는 None으로 설정됩니다.")

    except Exception as e:
        print(f"포스터, 공연 제목, 예매처 링크 로드 실패: {e}")

    # 추출한 결과 반환
    return poster_url, title, category, ticket_link, exclusive



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
    


# def crawl_open_page(driver, csoonID, valid_links):

#     # HTML 저장할 리스트
#     crawling_list = []

#     csoon_url = f"https://www.ticketlink.co.kr/help/notice/{csoonID}"
#     driver.get(csoon_url)
#     print(f"페이지 로드 완료: {driver.current_url}")
#     wait = WebDriverWait(driver, 20)

#     # 오픈예정 페이지 HTML 추출
#     try:
#         dl_list_view = driver.find_element(By.CLASS_NAME, "list_view").get_attribute("outerHTML")
#     except NoSuchElementException:
#         print(f"오픈예정 페이지의 HTML을 찾을 수 없습니다: csoonID={csoonID}")
#         dl_list_view = None

#     # 데이터 초기화
#     data = {
#         'poster_url': None, 'title': None, 'host' : {'link': None, 'site_id' : None}, 'start_date': None, 'end_date': None,
#         'show_time': None, 'location': None, 'region': None, 'price': [{'seat': None, 'price': None}], 'running_time': None, 'rating': None,
#         'open_date': None, 'pre_open_date': None, 'exclusive': 0, 'category': None, 'performance_description': None
#     }

#     artist_data = []  
#     cast_data = []
#     detail_html = None 

#     try:
#         # 전체 텍스트 추출
#         page_text = driver.find_element(By.TAG_NAME, "body").text

#         ################## 본문 공연 정보 추출 ##################
#         start_date, end_date, show_time, location, price, running_time, rating = extract_performance_info(page_text)

#         ################## 헤더 공연 정보 추출 ##################
#         poster_url, title, category, ticket_link, exclusive = extract_header(wait)

#         ################## 예매일 추출 ##################
#         open_date, pre_open_date = extract_open_date(driver, page_text)

#         ################## 공연 설명 추출 ##################
#         announcement_section = driver.find_element(By.CLASS_NAME, "list_view")
#         full_text = announcement_section.text.strip()
#         performance_description = extract_description(full_text)


#         region=crawl_with_retry(location)
        
#         # Price 전처리

#         seat = None 

#         def extract_seat_prices(price):
#             # 정규 표현식: 좌석과 가격을 추출
#             pattern = r'([A-Za-z가-힣]+(?:석)?(?:\([^\)]+\))?)\s*[-]?\(?(\d{1,3}(?:,\d{3})*)\s*원\)?|(\d{1,3}(?:,\d{3})*)\s*원'
            
#             result = []
#             #seat = None 
#             # '/'로 구분된 경우 처리
#             price_list = price.split(' / ')
            
#             for price_item in price_list:
#                 matches = re.findall(pattern, price_item.strip())
                
#                 if matches:
#                     for match in matches:
                        
#                         if match[0] and match[1]:  # 좌석과 가격이 모두 있는 경우
#                             seat = match[0].strip()
#                             price = int(match[1].replace(",", ""))
#                             price = "{:,.0f}".format(price)
#                         elif match[2]:  # 가격만 있는 경우
#                             seat = '일반석'
#                             price = int(match[2].replace(",", ""))
#                             price = "{:,.0f}".format(price)
                        
#                         price =  str(price)
#                         up_price = price.replace("원", "")
#                         up_price = up_price.strip() + "원"
#                         result.append({'seat': seat, 'price': up_price})


                    
#             # 가격 정보가 없다면, 'seat'와 'price' 모두 None인 항목 추가
#             if not result:
#                 return [{'seat': price_list, 'price': None}]
            
#             return result

#         price = extract_seat_prices(price)
        
#         # 데이터 업데이트
#         data.update({
#             'poster_url': poster_url, 'title': title, 'host' : {'site_id' : 3, 'link': ticket_link},
#             'start_date': start_date, 'end_date': end_date, 'show_time': show_time,
#             'location': location, 'region': region, 'price': price, 'running_time': running_time, 'rating': rating,
#             'open_date': open_date, 'pre_open_date': pre_open_date, 'exclusive': exclusive, 'category': category,
#             'performance_description': performance_description
#         })

#         print(f"\n공연 정보\n{data}\n")

#         # 예매 링크 존재 여부 확인
#         if ticket_link and ticket_link != None:
#             try:
#                 driver.get(ticket_link)
#                 print(f"\n*****추가 데이터 추출을 위해 페이지 이동: {ticket_link}*****\n")

#                 # 추가 정보 추출 (공연 세부 정보, 캐스트, 아티스트 데이터)
#                 wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '장소')]/following-sibling::div")))
#                 performance_update = extract_performance_data(driver)
#                 cast_data, artist_data = extract_cast_data(driver)

#                 # None인 값만 업데이트
#                 for key in ['title', 'location', 'running_time', 'start_date', 'end_date', 'rating', 'price']:
#                     if data[key] is None and performance_update.get(key) is not None:
#                         data[key] = performance_update[key]

#                 print(f"data 업데이트 완료\n{data}\n")
#                 print(f"cast_data\n{cast_data}\n")
#                 print(f"artist_data\n{artist_data}\n")

#                 # 상세 페이지 HTML 추출
#                 detail_html = extract_detail_html(driver)

#             except Exception as e:
#                 print(f"추가적으로 상세 페이지에서 정보 업데이트를 시도했지만 오류가 발생했습니다: {e}\n")
#                 ticket_link = None

#         else:
#             print("예매 링크가 없어 추가 정보를 가져올 수 없습니다.\n")

#     except Exception as e:
#         print(f"공연 정보 추출 중 오류 발생: {e}\n")

#     # 오픈예정 페이지와 상세 페이지 HTML을 crawling_list에 저장
#     crawling_list.append({"ID": f"{csoonID}", "HTML": str(dl_list_view)+str(detail_html)})

#     #print(f"crawling_list에 저장된 데이터: {crawling_list}")

#     # 예외 처리 - 추가적인 상세 페이지 정보 업데이트를 시도했지만 필요한 정보를 찾을 수 없을 때
#     if any(data[key] is None for key in ['location', 'running_time', 'start_date', 'end_date', 'rating', 'price']):
#         print("추가적으로 상세 페이지에서 정보 업데이트를 시도했지만 정보를 찾을 수 없습니다.\n")

#     #return data, cast_data, artist_data, crawling_list
#     return crawling_list