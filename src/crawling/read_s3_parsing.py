from kafka import KafkaProducer
import json
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil import parser
###################################################################region 함수 추가
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import kafka

def get_region(location):
    # 지역 맵
    region_map = {
        '서울': '서울',
        '경기': '수도권',
        '인천': '수도권',
        '부산': '경상',
        '대구': '경상',
        '울산': '경상',
        '경남': '경상',
        '경북': '경상',
        '전북': '전라',
        '전주': '전라',
        '광주': '전라',
        '전남': '전라',
        '충남': '충청',
        '충북': '충청',
        '대전': '충청',
        '강원': '강원',
        '제주': '제주',
    }


    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.20 Safari/537.36");
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")  # headless 있으면 동작안됌
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1920,1080")

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    link = f'https://map.kakao.com/?q={location}'
    try:
        driver.get(link)
        
        # 페이지 로딩 기다리기 (예: 주소가 로딩될 때까지 기다림)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-id='address']"))
        )

        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # p 태그에서 data-id='address'를 찾고, 텍스트 추출
        address_tag = soup.find('p', {'data-id': 'address'})
        if address_tag:
            address_text = address_tag.get_text().strip()  # 텍스트 추출
            print("주소:", address_text)

            # 지역 추출 및 매핑
            region = None
            for region_key in region_map:
                if region_key in address_text:
                    region = region_map[region_key]
                    break

            if region:
                print(f"해당 지역은 {region}입니다.")
                return region
            else:
                print("지역을 찾을 수 없습니다.")
                
        else:
            print("주소를 찾을 수 없습니다. 재검색을 시도합니다.")
            

    except Exception as e:
        print(f"접속 에러: {e}")
    finally:
        driver.quit()  # 브라우저 종료

def convert_to_datetime_format(date_str):
    # 예시: "2024년 11월 6일(수) 오후 2시"
    # 오후/오전을 처리하기 위한 정규식
    am_pm = 'AM' if '오전' in date_str else 'PM'

    # 월, 일, 시간, 분 추출
    date_str = re.sub(r'[^\d\s가-힣]', '', date_str)  # 숫자와 공백 외 문자 제거
    date_match = re.search(r'(\d{1,2})월 (\d{1,2})일.*?(\d{1,2})시', date_str)

    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        hour = int(date_match.group(3))

        # 오전/오후를 반영해 시간 조정 (12시간제 → 24시간제)
        if am_pm == 'PM' and hour != 12:
            hour += 12
        elif am_pm == 'AM' and hour == 12:
            hour = 0

        # 날짜 형식에 맞춰 변환
        current_year = datetime.now().year  # 현재 년도 추출
        formatted_date = f"{current_year:04d}.{month:02d}.{day:02d} {hour:02d}:00"
        return formatted_date
    return None

def html_parsing(base_file_number):
    aws_conn_id = 'data'  # Airflow 연결 ID
    bucket_name = 't1-tu-data'

    hook = S3Hook(aws_conn_id=aws_conn_id)

    #base_file_number = 52879  # 시작 파일 번호
    end_file_number = base_file_number + 2000  # 53531 # 끝 파일 번호 설정
    # 파일 번호를 하나씩 증가시키면서 반복 처리
    #while True:###################################################테스트
    while base_file_number <= end_file_number:
        s3_key_prefix = f'interpark/{base_file_number}'
        files = hook.list_keys(bucket_name, prefix=s3_key_prefix)

        found_base_file_number_ = None
        for file in files:
            if file.startswith(f'interpark/{base_file_number}_'):
                found_base_file_number_ = file
                break

        # 첫 번째 파일 처리
        if found_base_file_number_:
            print(f"Processing {found_base_file_number_}")
            file_html = hook.read_key(found_base_file_number_, bucket_name)
            soup = BeautifulSoup(file_html, 'html.parser')

            # 카테고리 (뮤지컬 등)
            category = soup.find('div', class_='tagText')
            if category:
                category_text = category.find_all('span')[0].text.strip()
                if not any(keyword in category_text for keyword in ["뮤지컬", "연극", "전시/행사", "콘서트"]):
                    print(f"{category_text}는 넘어갑니다.")
                    base_file_number += 1
                    continue

            # 예매하기 페이지에서 1차 데이터 추출
            ticket_data = extract_data(soup)
        
            # None 값이 남아있는 경우 base_file_number로 다시 추출
            if any(value is None for key, value in ticket_data.items() if key != "hosts"):
                print("Some values are None. Checking base file.")
                try:
                    base_file_html = hook.read_key(f'interpark/{base_file_number}.html', bucket_name)
                    #base_file_html = base_file_html.decode('utf-8')
                    base_soup = BeautifulSoup(base_file_html, 'html.parser')
               
                    # 제목 추출
                    info_title = base_soup.find('div', class_='info')
                    title = info_title.find('h3')
                    title = title.text.strip()
                    if title:
                        if ticket_data['title'] == None:
                            ticket_data['title'] = re.sub(r'\s+|[^\w가-힣0-9]', '', title)

                    # 공연기간 추출
                    introduce = base_soup.find('div', class_='introduce')
                    data = introduce.find('div', class_='data')
                    if data and ticket_data['start_date'] == None:
                        p = data.find('p').text.strip()
                        lines = p.strip().split('\n')
                        for line in lines:
                            line = line.replace(" ","").strip()
                            if "공연일시" in line or "일시" in line or "공연기간" in line or "공연일자" in line:
                                date = line.split(":")[1].split("~")  # ':' 이후를 가져오고 '~' 기준으로 분리
                                if len(data) ==1:
                                    start_date_raw = date[0].strip()
                                    end_date_raw = start_date_raw
                                else:
                                    start_date_raw = date[0].strip()
                                    end_date_raw = date[1].strip()
                                # 시작 날짜 처리 (2024년 12월 14일(토) -> 2024.12.14)
                                start_date_match = re.search(r'(\d{4})년(\d{1,2})월(\d{1,2})일', start_date_raw)
                                if start_date_match:
                                    start_date = f"{start_date_match.group(1)}.{int(start_date_match.group(2)):02d}.{int(start_date_match.group(3)):02d}"
                                    # 종료 날짜 처리 (12월 15일(일) -> 2024.12.15)
                                    end_date_match = re.search(r'(\d{1,2})월(\d{1,2})일', end_date_raw)
                                    if end_date_match:
                                        # start_date에서 년도 추출
                                        year_from_start = start_date_match.group(1)
                                        # end_date에 년도 추가
                                        end_date = f"{year_from_start}.{int(end_date_match.group(1)):02d}.{int(end_date_match.group(2)):02d}"
                                    ticket_data['start_date'] = start_date
                                    ticket_data['end_date'] = end_date

                    # 티켓오픈일, 선예매 추출
                    ticket_open_date = None
                    fanclub_preopen_date = None
                    li_elements = base_soup.find_all('li')
                    for li in li_elements:
                        strong_tag = li.find('strong')  # strong 태그 찾기
                        if strong_tag:
                            strong_text = strong_tag.text.strip()
                            if "티켓오픈일" in strong_text:
                                # 텍스트에서 날짜 추출
                                ticket_open_date = li.text.replace(strong_text, '').strip()
                                ticket_open_date = convert_to_datetime_format(ticket_open_date) ##
                            elif "선예매" in strong_text:
                                # 텍스트에서 날짜 추출
                                fanclub_preopen_date = li.text.replace(strong_text, '').strip()
                                fanclub_preopen_date = convert_to_datetime_format(fanclub_preopen_date)##
                    if ticket_open_date:
                        ticket_data['open_date'] = ticket_open_date
                    if fanclub_preopen_date:
                        ticket_data['pre_open_date'] = fanclub_preopen_date

                    # 링크 추출
                    book_link = base_soup.find('a', class_='btn_book')
                    if book_link and 'href' in book_link.attrs:
                        ticket_data['hosts'][0]['ticket_url'] = book_link['href']
                
                    # 설명 추출
                    desc = base_soup.find('div', class_='info1')
                    description = desc.find('div', class_='data')
                    if description:
                        description = description.text.strip()
                        ticket_data['description'] = description
        
                    producer = KafkaProducer(
                    bootstrap_servers = ['kafka1:9093','kafka2:9094', 'kafka3:9095'],
                    value_serializer=lambda x: json.dumps(x).encode('utf-8')
                    )
                    topic = 'interpark_data'
                    try:

                        # ticket_data 형식에 맞게 메시지 작성
                        message = {
                        "title": ticket_data["title"],
                        "duplicatekey":  ticket_data["duplicatekey"],
                        "category":  ticket_data["category"],
                        "location":  ticket_data["location"],
                        "region":  ticket_data["region"],
                        "price":  ticket_data["price"],
                        "start_date":  ticket_data["start_date"],
                        "end_date":  ticket_data["end_date"],
                        "running_time":  ticket_data["running_time"],
                        "casting":  ticket_data["casting"],
                        "rating":  ticket_data["rating"],
                        "description":  ticket_data["description"],
                        "poster_url":  ticket_data["poster_url"],
                        "open_date":  ticket_data["open_date"],
                        "pre_open_date":  ticket_data["pre_open_date"],
                        "artist":  ticket_data["artist"],
                        "hosts":  ticket_data["hosts"]
                        }

                        producer.send(topic, message)     
                        
                        print(message)
                        print(f'{base_file_number} insert complete')
                    except Exception as e:
                        print(f"message가 없습니다: {message}")
                    producer.flush()
                except Exception as e:
                        print(f"{base_file_html}에 연결 실패")        

        base_file_number+=1


def extract_data(soup):
    """BeautifulSoup 객체에서 데이터를 추출하는 함수"""
    ticket_data = {
        "title": None,
        "duplicatekey": None,
        "category": None,
        "location": None,
        "region": None,
        "price": None,
        "start_date": None,
        "end_date": None,
        "running_time": None,
        "casting": None,
        "rating": None,
        "description": None,
        "poster_url": None,
        "open_date": None,
        "pre_open_date": None,
        "artist": None,
        "hosts": [{"site_id": 1, "ticket_url": None}]
    }

    # 공연 제목
    title = soup.find('h2', class_='prdTitle')
    if title:
        ticket_data['title'] = title.text.replace('\n','').strip()

    # 카테고리
    category = soup.find('div', class_='tagText')
    if category:
        ticket_data['category'] = category.find_all('span')[0].text.strip()

    # 장소, 공연기간, 관람연령, 러닝타임
    li_range = soup.find_all('li', class_='infoItem')
    for li in li_range:
        text = li.text
        if "장소" in text:
            place = text.split("장소")[1].strip()
            ticket_data['location'] = place.split(' (자세히)')[0].replace('\n', '').strip()
        elif "공연기간" in text:
            date_range = text.split("공연기간")[1].strip()
            if "~" in date_range:
                start_date, end_date = date_range.split("~")
                ticket_data["start_date"] = start_date.strip()
                ticket_data["end_date"] = end_date.strip()
            else:
                ticket_data["start_date"] = ticket_data["end_date"] = date_range.strip()
        elif "관람연령" in text:
            ticket_data["rating"] = text.split("관람연령")[1].strip()
        elif "공연시간" in text:
            ticket_data["running_time"] = text.split("공연시간")[1].strip()
    
    # 중복 데이터 확인을 위한 키 추가 
    ticket_data['duplicatekey'] = re.sub(r'\s+|[^\w가-힣0-9]', '', title.text)+ticket_data['start_date']

    # 지역 추출
    location = ticket_data['location']
    ticket_data['region'] = get_region(location)
    if ticket_data['region'] is None:
        print("region 재검색중...")
        location_part = location.rsplit(' ',1)
        result = ' '.join(location_part[0][:2])
        ticket_data['region'] = get_region(result)
    
    # 가격 추출
    price_list = []
    price_elements = soup.find_all('li', class_='infoPriceItem')
    for price in price_elements:
        price_text = price.text.strip().split()
        if not any("자세히" in item for item in price_text):
            if len(price_text) >= 2:
                seat = price_text[:-1]
                price = price_text[-1]
                price_list.append({"seat": " ".join(seat), "price": price})
    ticket_data["price"] = price_list

    # 포스터 이미지 URL
    poster_url = soup.find('img', class_='posterBoxImage')
    if poster_url:
        ticket_data["poster_url"] = 'https:'+poster_url['src']
        if ticket_data["poster_url"] == None:
            src_url = soup.find('img', class_="poster bgConcert")
            if src_url and 'src' in src_url.attrs:
                print("*"*33)
                print(src_url.attrs)
                poster_url_src = src_url['src']
                ticket_data['poster_url'] = 'https:'+poster_url_src

    # 캐스팅 정보
    role_list = []
    role_name = soup.find_all('div', class_='castingActor')
    for role in role_name:
        role = role.text.replace('\n', '').strip()
        role_list.append({"role": role, "actor": None})
    actor_list = []
    actor_name = soup.find_all('div', class_='castingName')
    for actor in actor_name:
        actor = actor.text.replace('\n', '').strip()
        actor_list.append(actor)
    for i, role in enumerate(role_list):
        if i < len(actor_list):
            role["actor"] = actor_list[i]
    ticket_data['casting'] = role_list

    # 아티스트 정보
    artist_data = []
    urls = soup.find_all('div', class_='castingProfile')
    for i, url in enumerate(urls):
        if i < len(actor_list):
            img_tag = url.find('img', class_='castingImage')
            if img_tag and 'src' in img_tag.attrs:
                artist_url = 'https:'+img_tag['src']
                artist_data.append({"artist_name": actor_list[i],
                                    "artist_url": artist_url})
    ticket_data['artist'] = artist_data
    return ticket_data

# 함수 실행
#html_parsing(52879)
