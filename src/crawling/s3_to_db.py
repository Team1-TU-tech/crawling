from detail_page import *
from open_page import *
from valid_links import *

def crawl_data(driver, csoonID, valid_links):

    csoon_url = f"https://www.ticketlink.co.kr/help/notice/{csoonID}"
    driver.get(csoon_url)
    print(f"페이지 로드 완료: {driver.current_url}")
    wait = WebDriverWait(driver, 20)

    artist_data = []  
    cast_data = []

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

        # Region 전처리
        region=crawl_region(location)
        
        # Price 전처리
        price = extract_seat_prices(price)
        
        duplicate_key = f"{title}{start_date}"

        data = {
            "title": title,
            "duplicatekey": duplicate_key,
            "category": category,
            "location": location,
            "price": price,
            "start_date": start_date,
            "end_date": end_date,
            "running_time": running_time,
            "casting": None,
            "rating": rating,
            "description": performance_description,
            "poster_url": poster_url,
            "region": region,
            "open_date": None,
            "pre_open_date": None,
            "artist": artist_data,
            "hosts": [{"site_id": 2, "ticket_url": ticket_url}]
        }

artist_data = []  
    cast_data = []
        # 예매 링크 존재 여부 확인
        if ticket_link and ticket_link != None:
            try:
                driver.get(ticket_link)
                print(f"\n*****추가 데이터 추출을 위해 페이지 이동: {ticket_link}*****\n")

                # 추가 정보 추출 (공연 세부 정보, 캐스트, 아티스트 데이터)
                wait.until(EC.presence_of_element_located((By.XPATH, "//ul[@class='product_info_list type_col2']//span[contains(text(), '장소')]/following-sibling::div")))
                performance_update = extract_performance_data(driver)
                cast_data, artist_data = extract_cast_data(driver)

                # None인 값만 업데이트
                for key in ['title', 'location', 'running_time', 'start_date', 'end_date', 'rating', 'price']:
                    if data[key] is None and performance_update.get(key) is not None:
                        data[key] = performance_update[key]

                print(f"data 업데이트 완료\n{data}\n")
                print(f"cast_data\n{cast_data}\n")
                print(f"artist_data\n{artist_data}\n")

            except Exception as e:
                print(f"추가적으로 상세 페이지에서 정보 업데이트를 시도했지만 오류가 발생했습니다: {e}\n")
                ticket_link = None

        else:
            print("예매 링크가 없어 추가 정보를 가져올 수 없습니다.\n")

    except Exception as e:
        print(f"공연 정보 추출 중 오류 발생: {e}\n")


    # 예외 처리 - 추가적인 상세 페이지 정보 업데이트를 시도했지만 필요한 정보를 찾을 수 없을 때
    if any(data[key] is None for key in ['location', 'running_time', 'start_date', 'end_date', 'rating', 'price']):
        print("추가적으로 상세 페이지에서 정보 업데이트를 시도했지만 정보를 찾을 수 없습니다.\n")

    return data, cast_data, artist_data



def main():
    valid_links = collect_valid_links()

    if valid_links:
        data = crawl_data(valid_links)
        print(f"data는 다음과 같습니다: {data}")
        return data
    else:
        print("수집된 유효한 링크가 없습니다.")
        return []

if __name__ == "__main__":
    main()