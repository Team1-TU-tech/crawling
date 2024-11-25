from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time

def get_link(start_id=50016):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저를 띄우지 않고 실행
    options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 사용 비활성화
    options.add_argument('--no-sandbox')  # 샌드박스 모드 비활성화 (Docker 환경에서 권장)  
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 링크를 저장할 리스트
    all_links = []
    num = start_id  # 시작할 start_id 가져오기
    print(f"크롤링 시작: 시작 페이지 번호는 {num}입니다.")
    
    try:
        while True:
            url = f'http://ticket.yes24.com/Perf/{num}'
            print(f"페이지 수집 중: {url}")
            driver.get(url)
            time.sleep(3)  # 페이지 로딩 대기

            try:
                # 에러 페이지 확인
                error_image = driver.find_elements(By.CSS_SELECTOR, 'img[src="http://tkfile.yes24.com/images/errorImg_ticket.gif"]')

                if error_image:
                    if num >= 51600:  # 마지막 페이지 조건
                        print(f"마지막 페이지 {num}에서 크롤링을 종료합니다.")
                        break
                    else:
                        print(f"페이지 {num}은 삭제된 페이지입니다. 다음 페이지로 이동합니다.")
                else:
                    # 정상 페이지라면 링크를 저장
                    print(f"페이지 {num} 수집 완료.")
                    all_links.append(url)

            except Exception as e:
                print(f"페이지 {num}에서 오류 발생: {e}")
                break  # 에러 발생 시 크롤링 종료

            # 다음 페이지로 이동
            num += 1

    except KeyboardInterrupt:
        print("\n작업이 중단되었습니다. 마지막으로 시도한 페이지 번호를 저장합니다.")
    finally:
        driver.quit()

    # 크롤링 결과 출력
    print(f"총 {len(all_links)}개의 링크를 수집했습니다.")
    return all_links


# 실행
if __name__ == "__main__":
    get_link = get_link()
