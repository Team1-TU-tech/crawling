from selenium.webdriver.common.by import By
from crawling.utils import get_offset, set_offset
import time

def get_link(driver):

    # 링크를 저장할 리스트
    all_links = []
    num = get_offset()
    previous_page_error = True  # 이전 페이지가 에러인지를 확인하는 변수

    try:
        while True:
            # 공연 상세 페이지 열기
            url = f'http://ticket.yes24.com/Perf/{num}'
            driver.get(url)
            print(f"페이지 수집 중: 페이지 {url}")

            # 페이지 로딩 대기
            time.sleep(3)
            num += 1
            
    #         try:
    #             error_image = driver.find_elements(By.CSS_SELECTOR, 'img[src="http://tkfile.yes24.com/images/errorImg_ticket.gif"]')

    #             if error_image:  # 에러 페이지인 경우
    #                 if previous_page_error:  # 이전 페이지가 에러였다면
    #                     print(f"이전 페이지 {num - 1}도 에러였고, 현재 페이지 {num}도 에러입니다. 건너뜁니다.")
    #                     num += 1
    #                     continue  # 계속 진행

    #                 else:  # 이전 페이지가 에러가 아니었으면 종료
    #                     print(f"이전 페이지 {num - 1}는 정상적이었고, 현재 페이지 {num}는 404 오류입니다. 종료합니다.")
    #                     try:
    #                         set_offset(num)  # 종료 전, 마지막으로 시도한 페이지를 offset으로 저장
    #                     except Exception as e:
    #                         print(f"오프셋 저장 중 오류 발생: {e}")

    #                     # 다음 페이지가 정상인지 확인하기 위한 코드
    #                     next_url = f'http://ticket.yes24.com/Perf/{num + 1}'
    #                     driver.get(next_url)
    #                     time.sleep(1)
    #                     next_error_image = driver.find_elements(By.CSS_SELECTOR, 'img[src="http://tkfile.yes24.com/images/errorImg_ticket.gif"]')

    #                     if not next_error_image:  # 다음 페이지가 정상적인 경우
    #                         print(f"다음 페이지 {num + 1}는 정상적입니다. 계속 진행합니다.")
    #                         num += 1
    #                         continue  # 계속해서 다음 페이지로 진행
                        
    #                     elif num < 50000:
    #                         print(f"페이지가 존재하지 않지만 마지막 페이지가 아니므로 계속 진행합니다.")
    #                         num += 1
    #                         continue  # num이 50000 미만이면 계속 진행
                        
    #                     else:
    #                         break  # 다음 페이지도 에러라면 종료

    #             else:  # 에러가 아닌 경우
    #                 # 정상적인 페이지라면 링크를 리스트에 추가
    #                 all_links.append(url)

    #                 # 페이지 번호 증가
    #                 num += 1
    #                 previous_page_error = False  # 이전 페이지가 정상적이면 에러 플래그 리셋
            
    #         except Exception as e:
    #             print(f"페이지 {num}에서 오류 발생: {e}")
    #             set_offset(num)  # 종료 전, 마지막으로 시도한 페이지를 offset으로 저장
    #             break  # 오류 발생 시 크롤링 종료

    except KeyboardInterrupt:
        # 키보드 인터럽트가 발생한 경우 오프셋 저장 후 종료
        print("\n작업이 중단되었습니다. 마지막 페이지 번호를 저장합니다.")
        set_offset(num)

    # 크롬 드라이버 종료
    set_offset(num)
    driver.quit()

    # 링크 리스트 출력
    print(f"총 {len(all_links)}개의 링크를 수집했습니다.")
    return all_links

