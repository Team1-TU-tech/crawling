# ticket link crawling

# USAGE
## 1. 프로젝트 클론
```
git clone <repository_url>
cd <repository_directory>
```

## 2. 가상환경 활성화
```
source .venv/bin/activate
```

## 3. 라이브러리 설치
```
pdm install
```

## 4. 크롤링 실행
```
python valid_links.py
```

# Code Description
## valid_links.py
- extract_last_id: base_url 페이지에서 첫 번째 공연 ID를 찾아 크롤링 범위 마지막이 될 **고유 번호 추출**.
- crawl_ID: 특정 csoonID에 대해 공연의 카테고리, 예매 링크 등을 크롤링하여 **유효한 링크를 valid_links 리스트에 저장**.
- **collect_valid_links**: extract_last_id()에서 가져온 마지막 ID를 기준으로, **csoonID 범위를 설정하고 크롤링하여 유효한 링크를 수집**.
- **crawl_valid_links**: collect_valid_links()에서 수집한 유효한 링크를 바탕으로 공연에 대한 **상세 데이터를 크롤링**.

## open_page.py
- normalize_date: 주어진 날짜 형식을 **YYYY.MM.DD 형식으로 표준화**. 
- normalize_datetime: 날짜와 시간을 포함하는 텍스트에서 시간을 추출하여 **YYYY.MM.DD HH:MM 형식으로 표준화**. 오전/오후, 시분 등의 정보도 처리하며 시/분은 선택.
- extract_description: **공연 설명 부분 추출**. 특정 키워드를 기준으로 설명 영역을 구분하고, 설명을 반환.
- extract_performance_info: **공연 시간, 장소, 가격, 관람 시간**와 같은 정보를 본문에서 추출.
- extract_header: **포스터 URL, 제목, 예매처 링크, 카테고리**와 같은 정보를 헤더 정보에서 추출.
- extract_open_date: 텍스트에서 특정 키워드를 찾아 해당 날짜 정보를 처리하여 **예매일과 선예매일** 추출. 
- **crawl_open_page: 주어진 URL에서 공연 정보를 크롤링.**
  - 주어진 공연 ID에 해당하는 티켓 링크에서 공연 정보를 크롤링하여, 공연의 기본 정보, 추가 정보(캐스트, 아티스트), 그리고 상세 HTML을 추출한 후 이를 반환

## detail_page.py
- extract_performance_data: **공연 정보(장소, 관람시간, 기간, 관람등급, 가격 정보)** 추출
- extract_cast_data: **캐스팅 및 아티스트 정보** 추출
- extract_detail_html: **페이지의 전체 HTML** 추출
- 
## offset.py
offset.ini 파일을 통해 설정된 **offset** 값을 관리하고, 없을 경우 **기본값**을 설정.
크롤링이 중단되는 지점에서 offset 값을 기록하고, 이후 다시 시작할 때 해당 offset 값을 기준으로 크롤링을 재개.
