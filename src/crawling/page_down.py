def page_down(driver, time):
    # 페이지 높이를 가져와서 점진적으로 스크롤 다운
    scroll_pause_time = 5  # 전체 스크롤 시간 (초)
    scroll_step = 200  # 한 번에 내릴 스크롤 거리
    last_height = driver.execute_script("return document.body.scrollHeight")
    start_time = time.time()

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time >= scroll_pause_time:
            break  # 5초가 지나면 종료
    
        # 스크롤 내리기
        driver.execute_script(f"window.scrollBy(0, {scroll_step})")
        # 페이지 높이가 변경되었는지 체크
        new_height = driver.execute_script("return document.body.scrollHeight")
    
        # 더 이상 스크롤을 내릴 곳이 없으면 종료
        if new_height == last_height:
            break
    
        # 새로 업데이트된 페이지 높이를 last_height로 설정
        last_height = new_height
    
        # 잠시 대기
        time.sleep(3)  # 페이지가 로딩될 수 있도록 잠시 대기

    # 추가 로딩이 끝날 때까지 대기
    time.sleep(2)

    # 마지막으로 로딩된 요소가 화면에 나타날 때까지 기다리기 (최대 10초 대기)
    driver.execute_script("window.scrollBy(0, 1000)")  # 마지막까지 스크롤을 한 번 더 내림
    time.sleep(2)

    return True