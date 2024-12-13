from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time

def get_link(start_id=52001, max_retries=3, retry_delay=5):
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
            retries = 0  # 재시도 횟수 초기화
            success = False  # 성공 여부 플래그

            while retries < max_retries and not success:
                try:
                    print(f"페이지 수집 중: {url} (시도 {retries + 1}/{max_retries})")
                    driver.get(url)
                    time.sleep(3)  # 페이지 로딩 대기

                    # 에러 페이지 확인
                    error_image = driver.find_elements(By.CSS_SELECTOR, 'img[src="http://tkfile.yes24.com/images/errorImg_ticket.gif"]')

                    if error_image:
                        if num >= 52000:  # 마지막 페이지 조건
                            print(f"마지막 페이지 {num}에서 크롤링을 종료합니다.")
                            return all_links
                        else:
                            print(f"페이지 {num}은 삭제된 페이지입니다. 다음 페이지로 이동합니다.")
                            success = True  # 다음 페이지로 이동하기 위해 성공 처리
                    else:
                        # 정상 페이지라면 링크를 저장
                        print(f"페이지 {num} 수집 완료.")
                        all_links.append(url)
                        success = True  # 성공 처리

                except WebDriverException as e:
                    retries += 1
                    print(f"WebDriver 예외 발생: {e}. {retry_delay}초 후 재시도합니다.")
                    time.sleep(retry_delay)
                except Exception as e:
                    print(f"알 수 없는 오류 발생: {e}.")
                    break  # 알 수 없는 예외 발생 시 크롤링 중단

            if not success:
                print(f"페이지 {num} 크롤링 실패. 다음 페이지로 이동합니다.")

            # 다음 페이지로 이동
            num += 1

    except KeyboardInterrupt:
        print("\n작업이 중단되었습니다. 마지막으로 시도한 페이지 번호를 저장합니다.")
    except Exception as e:
        print(f"예기치 못한 오류 발생: {e}")
    finally:
        driver.quit()

    # 크롤링 결과 출력
    print(f"총 {len(all_links)}개의 링크를 수집했습니다.")
    return all_links


# 실행
if __name__ == "__main__":
    get_link = get_link()

