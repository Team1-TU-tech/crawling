from src.crawling.detail_page import *
from src.crawling.open_page import *
from src.crawling.valid_links import *


def crawl_open_page(driver, csoonID, valid_links):

    # HTML 저장할 리스트
    crawling_list = []

    csoon_url = f"https://www.ticketlink.co.kr/help/notice/{csoonID}"
    driver.get(csoon_url)
    print(f"페이지 로드 완료: {driver.current_url}")
    wait = WebDriverWait(driver, 20)

    # 오픈예정 페이지 HTML 추출
    try:
        dl_list_view = driver.find_element(By.CLASS_NAME, "list_view").get_attribute("outerHTML")
    except NoSuchElementException:
        print(f"오픈예정 페이지의 HTML을 찾을 수 없습니다: csoonID={csoonID}")
        dl_list_view = None

    # 데이터 초기화
    data = {
        'poster_url': None, 'title': None, 'host' : {'link': None, 'site_id' : None}, 'start_date': None, 'end_date': None,
        'show_time': None, 'location': None, 'region': None, 'price': [{'seat': None, 'price': None}], 'running_time': None, 'rating': None,
        'open_date': None, 'pre_open_date': None, 'exclusive': 0, 'category': None, 'performance_description': None
    }

    artist_data = []  
    cast_data = []
    detail_html = None 

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


        region=crawl_region(location)
        
        # Price 전처리

        seat = None 

        def extract_seat_prices(price):
            # 정규 표현식: 좌석과 가격을 추출
            pattern = r'([A-Za-z가-힣]+(?:석)?(?:\([^\)]+\))?)\s*[-]?\(?(\d{1,3}(?:,\d{3})*)\s*원\)?|(\d{1,3}(?:,\d{3})*)\s*원'
            
            result = []
            #seat = None 
            # '/'로 구분된 경우 처리
            price_list = price.split(' / ')
            
            for price_item in price_list:
                matches = re.findall(pattern, price_item.strip())
                
                if matches:
                    for match in matches:
                        
                        if match[0] and match[1]:  # 좌석과 가격이 모두 있는 경우
                            seat = match[0].strip()
                            price = int(match[1].replace(",", ""))
                            price = "{:,.0f}".format(price)
                        elif match[2]:  # 가격만 있는 경우
                            seat = '일반석'
                            price = int(match[2].replace(",", ""))
                            price = "{:,.0f}".format(price)
                        
                        price =  str(price)
                        up_price = price.replace("원", "")
                        up_price = up_price.strip() + "원"
                        result.append({'seat': seat, 'price': up_price})


                    
            # 가격 정보가 없다면, 'seat'와 'price' 모두 None인 항목 추가
            if not result:
                return [{'seat': price_list, 'price': None}]
            
            return result

        price = extract_seat_prices(price)
        
        # 데이터 업데이트
        data.update({
            'poster_url': poster_url, 'title': title, 'host' : {'site_id' : 3, 'link': ticket_link},
            'start_date': start_date, 'end_date': end_date, 'show_time': show_time,
            'location': location, 'region': region, 'price': price, 'running_time': running_time, 'rating': rating,
            'open_date': open_date, 'pre_open_date': pre_open_date, 'exclusive': exclusive, 'category': category,
            'performance_description': performance_description
        })

        print(f"\n공연 정보\n{data}\n")

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

    #print(f"crawling_list에 저장된 데이터: {crawling_list}")

    # 예외 처리 - 추가적인 상세 페이지 정보 업데이트를 시도했지만 필요한 정보를 찾을 수 없을 때
    if any(data[key] is None for key in ['location', 'running_time', 'start_date', 'end_date', 'rating', 'price']):
        print("추가적으로 상세 페이지에서 정보 업데이트를 시도했지만 정보를 찾을 수 없습니다.\n")

    return cast_data, artist_data


def main():
    valid_links = collect_valid_links()

    if valid_links:
        cast_data, artist_data = crawl_open_page(valid_links)
        print(f"raw_html은 {cast_data} 다음과 같습니다!")
        print(f"raw_html은 {artist_data} 다음과 같습니다!")
        return cast_data, artist_data
    
    else:
        print("수집된 유효한 링크가 없습니다.")
        return []

if __name__ == "__main__":
    main()