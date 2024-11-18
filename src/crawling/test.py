import requests
from bs4 import BeautifulSoup
from utils import set_offset  # set_offset 함수 임포트
from links import get_link

def scrape_data():
    # 크롤링할 데이터 저장용 리스트
    data = []
    all_links = ['http://ticket.yes24.com/Perf/51671'] 
    #all_links = get_link()  # get_link()에서 가져온 링크들

    for link in all_links:
        print(f"크롤링 중: {link}")

        # HTTP 요청을 보내 페이지 내용 가져오기
        response = requests.get(link)

        # 페이지가 정상적으로 로드되었는지 확인
        if response.status_code != 200:
            print(f"페이지 로드 실패: {link} (상태 코드: {response.status_code})")
            continue

        # BeautifulSoup을 이용하여 페이지 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            # 카테고리
            category = soup.select_one('.rn-location a').text if soup.select_one('.rn-location a') else None
            # 단독판매 여부
            exclusive_sales = soup.select_one('.rn-label').text if soup.select_one('.rn-label') else None
            # 공연 제목
            title = soup.select_one('.rn-big-title').text if soup.select_one('.rn-big-title') else None
            # 공연 시간
            performance_time = soup.select_one('.rn-product-area3 dd').text if soup.select_one('.rn-product-area3 dd') else None

            # 공연 상세 정보
            performance_details = soup.select('.rn08-tbl td')
            running_time = performance_details[5].text if len(performance_details) > 5 else None
            age_rating = performance_details[4].text if len(performance_details) > 4 else None
            performance_place = performance_details[6].text if len(performance_details) > 6 else None

            # 가격 정보
            price_elements = soup.select('#divPrice .rn-product-price1')
            price = price_elements[0].text if price_elements else None
            # 포스터 이미지 URL
            poster_img = soup.select_one('.rn-product-imgbox img')['src'] if soup.select_one('.rn-product-imgbox img') else None
            # 출연진 정보
            performers = soup.select('.rn-product-peole')

            performer_names = []
            performer_links = []

            for performer in performers:
                performer_names.append(performer.text)  # 이름 추출
                performer_links.append(performer.get('href'))  # 링크 추출

            # 출연진이 없을 경우 None으로 설정
            if not performer_names:
                performer_names.append(None)
                performer_links.append(None)

            # 호스팅 서비스 사업자 정보
            hosting_provider = soup.select_one('.footxt p').text if soup.select_one('.footxt p') else None
            # 기획사 정보
            # 'divPerfOrganization' ID를 가진 td 요소 찾기
            organizer_info = soup.select_one('#divPerfOrganization')

            # 디버깅: organizer_info 출력
            print("organizer_info 내용:")
            print(organizer_info)  # 실제로 선택된 요소 확인

            # 텍스트가 있을 경우 <br> 기준으로 나누어 주최와 주관 정보 추출
            if organizer_info:
                organizer_text = organizer_info.get_text(separator=' ', strip=True)
                print(f"organizer_text: {organizer_text}")

            # 주최, 주관 정보 분리
                organizer_split = organizer_text.split('주관:')
                host = organizer_split[0].replace('주최:', '').strip() if len(organizer_split) > 0 else None
                sponsor = organizer_split[1].strip() if len(organizer_split) > 1 else None
            else:
                host = None
                sponsor = None

            # 결과 출력
            print(f"주최: {host}")
            print(f"주관: {sponsor}")
            # 데이터를 리스트에 추가
            data.append({
                'category': category,
                'title': title,
                'age_rating': age_rating,
                'exclusive_sales': exclusive_sales,
                'performance_time': performance_time,
                'price': price,
                'performance_place': performance_place,
                'running_time': running_time,
                'poster_img': poster_img,
                'performer_names': performer_names,
                'performer_links': performer_links,
                'hosting_provider': hosting_provider,
                'organizer': organizer_info,
            })

            print(data)  # 크롤링된 데이터 출력

        except Exception as e:
            print(f"페이지에서 오류 발생: {e}")
            continue  # 오류가 발생해도 계속해서 다음 링크를 크롤링

    # 최종적으로 데이터 리턴
    return data

# 실행
if __name__ == "__main__":
    scraped_data = scrape_data()

