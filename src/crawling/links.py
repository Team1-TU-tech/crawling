from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Chrome 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저를 띄우지 않고 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_link():
    # 링크를 저장할 리스트
    all_links = []
    num = 1

    while True:
        print(f"크롤링 중: 페이지 {num}")

        # 공연 상세 페이지 열기
        url = f'http://ticket.yes24.com/Perf/{num}'
        driver.get(url)

        # 페이지 로딩 대기
        time.sleep(3)

        try:
            # 404 오류 페이지를 감지하기 위해 이미지 검사
            error_image = driver.find_elements(By.CSS_SELECTOR, 'img[src="http://tkfile.yes24.com/images/errorImg_ticket.gif"]')

            # 에러 페이지인 경우
            if error_image:
                print(f"페이지 {num}는 404 오류입니다. 건너뜁니다.")
                num += 1
                continue  # 404 오류 페이지는 건너뛰고, 다음 페이지로 진행

            # 정상적인 페이지라면 링크를 리스트에 추가
            all_links.append(url)

            # 페이지 번호 증가
            num += 1

        except Exception as e:
            print(f"페이지 {num}에서 오류 발생: {e}")
            break  # 오류 발생 시 크롤링 종료

    # 크롬 드라이버 종료
    driver.quit()

    # 링크 리스트 출력
    print(f"총 {len(all_links)}개의 링크를 수집했습니다.")
    print(all_links)

    return all_links
