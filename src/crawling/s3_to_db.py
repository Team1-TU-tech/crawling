from detail_page import *
from open_page import *
from valid_links import *

def crawl_data(driver, csoonID, valid_links):

    csoon_url = f"https://www.ticketlink.co.kr/help/notice/{csoonID}"
    driver.get(csoon_url)
    print(f"페이지 로드 완료: {driver.current_url}")
    wait = WebDriverWait(driver, 20)

    try:
        # 전체 텍스트 추출
        page_text = driver.find_element(By.TAG_NAME, "body").text

        ################## 본문 공연 정보 추출 ##################
        start_date, end_date, _, location, price, running_time, rating = extract_performance_info(page_text)

        ################## 헤더 공연 정보 추출 ##################
        poster_url, title, category, ticket_link, _ = extract_header(wait)

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
        
        if title:
            title_strip = re.sub(r'[^가-힣A-Za-z0-9]', '',title.strip())
        else:
            title_strip = None

        duplicate_key = f"{title_strip}{start_date}"


        artist_data = []  
        cast_data = []


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
            "casting": cast_data,
            "rating": rating,
            "description": performance_description,
            "poster_url": poster_url,
            "open_date": open_date,
            "pre_open_date": pre_open_date,
            "artist": artist_data,
            "hosts": [{"site_id": 3, "ticket_url": ticket_link}]
        }

        # 예매 링크 존재 여부 확인
        if ticket_link:
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

                data['casting'] = cast_data
                data['artist'] = artist_data

                print(f"data 업데이트 완료\n{data}\n")
                # print(f"cast_data\n{cast_data}\n")
                # print(f"artist_data\n{artist_data}\n")

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

    # # 데이터 출력
    # print("\n***** 최종 데이터 출력 *****")
    # for key, value in data.items():
    #     print(f"{key}: {value}")

    return data


def crawl_valid_links(valid_links):
    driver = initialize_driver()

    try:
        for link in valid_links:
            csoonID = link['csoonID']
            try:
                print(f"\nopen_page 데이터 수집을 시작합니다: csoonID = {csoonID}")
                
                # crawl_data 함수 호출 및 data 출력
                data = crawl_data(driver, csoonID, valid_links)
                
                # data 딕셔너리 출력
                print("\n***** crawl_data에서 수집한 데이터 *****")
                for key, value in data.items():
                    print(f"{key}: {value}")
                
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
