from detail_page import *
from open_page import *
from valid_links import *
import certifi
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import re

MONGO_URL="mongodb+srv://hahahello777:VIiYTK9NobgeM1hk@cluster0.5vlv3.mongodb.net/test?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
db = client.tut

def crawl_data(driver, csoonID):
    csoon_url = f"https://www.ticketlink.co.kr/help/notice/{csoonID}"
    driver.get(csoon_url)
    print(f"페이지 로드 완료: {driver.current_url}")
    wait = WebDriverWait(driver, 20)

    try:
        # 전체 텍스트 추출
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
        except Exception as e:
            print(f"페이지 텍스트를 찾을 수 없습니다: {e}")
            page_text = None

        ################## 본문 공연 정보 추출 ##################
        try:
            start_date, end_date, _, location, price, running_time, rating = extract_performance_info(page_text)
        except Exception as e:
            print(f"공연 정보 추출 실패: {e}")
            start_date, end_date, location, price, running_time, rating = None, None, None, None, None, None

        ################## 헤더 공연 정보 추출 ##################
        try:
            poster_url, title, category, ticket_link, _ = extract_header(wait)
        except Exception as e:
            print(f"헤더 정보 추출 실패: {e}")
            poster_url, title, category, ticket_link = None, None, None, None

        ################## 예매일 추출 ##################
        try:
            open_date, pre_open_date = extract_open_date(driver, page_text)
        except Exception as e:
            print(f"예매일 정보 추출 실패: {e}")
            open_date, pre_open_date = None, None

        ################## 공연 설명 추출 ##################
        try:
            announcement_section = driver.find_element(By.CLASS_NAME, "list_view")
            full_text = announcement_section.text.strip()
            performance_description = extract_description(full_text)
        except Exception as e:
            print(f"공연 설명 추출 실패: {e}")
            performance_description = None

        # Region 전처리
        try:
            region = crawl_region(location)
        except Exception as e:
            print(f"지역 정보 추출 실패: {e}")
            region = None

        # Price 전처리
        try:
            price = extract_seat_prices(price)
        except Exception as e:
            print(f"가격 정보 전처리 실패: {e}")
            price = None

        if title:
            title_strip = re.sub(r'[^가-힣A-Za-z0-9]', '', title.strip())
        else:
            title_strip = None

        duplicate_key = f"{title_strip}{start_date}"

        # 데이터 생성
        data = {
            "title": title,
            "duplicatekey": duplicate_key,
            "category": category,
            "location": location,
            "region": region,
            "price": price,
            "start_date": start_date,
            "end_date": end_date,
            "running_time": running_time,
            "casting": [],
            "rating": rating,
            "description": performance_description,
            "poster_url": poster_url,
            "open_date": open_date,
            "pre_open_date": pre_open_date,
            "artist": [],
            "hosts": [{"site_id": 3, "ticket_url": ticket_link}],
        }

        # 중복된 데이터가 존재하는지 체크
        try:
            existing_data = db.data.find_one({"duplicatekey": duplicate_key})

            if existing_data is None:
                # 새로운 데이터 삽입
                print(f"🐢🐢🐢🐢🐢Inserting new data: {duplicate_key}🐢🐢🐢🐢🐢")
                db.data.insert_one(data)
                existing_data = db.data.find_one({"duplicatekey": duplicate_key})
            else:
                # 중복된 데이터가 있으면 먼저 hosts 필드만 업데이트
                print(f"🥔🥔🥔🥔🥔Duplicate Data: {duplicate_key}. Updating hosts.🥔🥔🥔🥔🥔\n")
                previous_hosts = existing_data.get("hosts", [])
                if {"site_id": 3, "ticket_url": ticket_link} not in previous_hosts:
                    if len(previous_hosts) < 3:
                        previous_hosts.append({"site_id": 3, "ticket_url": ticket_link})
                        db.data.update_one({"duplicatekey": duplicate_key}, {"$set": {"hosts": previous_hosts}})
                
            # 그후 예매 상세 페이지가 있을 시 None 인 값에 대하여 업데이트 시도
            if ticket_link:
                try:
                    driver.get(ticket_link)
                    print(f"\n🎁🎁🎁추가 데이터 추출을 위해 페이지 이동: {ticket_link}🎁🎁🎁\n")

                    # 추가 정보 추출
                    wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '장소')]/following-sibling::div")))
                    performance_update = extract_performance_data(driver)
                    cast_data, artist_data = extract_cast_data(driver)

                    # 업데이트 할 필드 딕셔너리
                    fields_to_update = {}
                    for key in ['title', 'location', 'running_time', 'start_date', 'end_date', 'rating', 'price']:
                        if existing_data.get(key) in [None, ""] and performance_update.get(key):
                            fields_to_update[key] = performance_update[key]
                            
                    # casting 및 artist 데이터 병합
                    if cast_data and not existing_data.get("casting"):
                        fields_to_update['casting'] = cast_data

                    if artist_data and not existing_data.get("artist"):
                        fields_to_update['artist'] = artist_data

                    # 필요한 값만 업데이트
                    if fields_to_update:
                        db.data.update_one({"duplicatekey": duplicate_key}, {"$set": fields_to_update})
                        print(f"🍀🍀🍀🍀🍀Partial data updated for {duplicate_key}: {fields_to_update}🍀🍀🍀🍀🍀")
                    else:
                        print(f"✅ No updates required for {duplicate_key}.")       
                        
                except Exception as e:
                    print(f"DEBUG: existing_data: {existing_data}")
                    print(f"DEBUG: performance_update: {performance_update}")
                    print(f"DEBUG: cast_data: {cast_data}, artist_data: {artist_data}")

                    print(f"추가적으로 상세 페이지에서 정보 업데이트를 시도했지만 오류가 발생했습니다: {e}\n")

        except Exception as e:
            print(f"DB 처리 중 오류 발생: {e}\n")

    except Exception as e:
        print(f"전체 데이터 수집 중 예외 발생: {e}\n")

    return data



def crawl_valid_links(valid_links):
    driver = initialize_driver()

    try:
        for link in valid_links:
            csoonID = link['csoonID']
            try:
                print(f"\nopen_page 데이터 수집을 시작합니다: csoonID = {csoonID}")
                
                # crawl_data 함수 호출 및 data 출력
                data = crawl_data(driver, csoonID)
                
                # # data 딕셔너리 출력
                # print("\n***** crawl_data에서 수집한 데이터 *****")
                # for key, value in data.items():
                #     print(f"{key}: {value}")
                
            except Exception as e:
                print(f"오류 발생: csoonID = {csoonID}, 오류: {e}")
                continue
    except Exception as e:
        print(f"전체 프로세스 중단 오류: {e}")
    finally:
        driver.quit()
        print("추가 데이터 수집 완료!")

def main():
    valid_links = collect_valid_links()

    if valid_links:
        crawl_valid_links(valid_links)
    else:
        print("수집된 유효한 링크가 없습니다.")

if __name__ == "__main__":
    main()


