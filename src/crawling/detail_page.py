from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import time

# Chrome WebDriver setup (make sure you have installed ChromeDriver and it's in your PATH)
driver = webdriver.Chrome()

# URL to be scraped
url = "https://www.ticketlink.co.kr/product/52656"
driver.get(url)

try:
    time.sleep(3)
    main_content = driver.find_element(By.CLASS_NAME, 'common_container.page_detail')
    main_content_html = main_content.get_attribute('outerHTML')

    cast_data = []
    artist_data = []

    while True:
        # 현재 페이지에서 모든 출연진 요소 찾기
        cast_list = main_content.find_elements(By.CLASS_NAME, 'product_casting_item')

        for cast in cast_list:
            try:
                # 이미지 URL, 이름, 배역 추출
                img_element = cast.find_element(By.CLASS_NAME, 'product_casting_imgbox').find_element(By.TAG_NAME, 'img')
                img_url = img_element.get_attribute('src')
                
                name = cast.find_element(By.CLASS_NAME, 'product_casting_name').text.strip()
                role = cast.find_element(By.CLASS_NAME, 'product_casting_role').text.strip()
                
                # cast_data와 artist_data 리스트에 이미 추가되지 않은 경우 데이터 추가
                if {'name': name, 'role': role} not in cast_data:
                    cast_data.append({
                        'name': name,
                        'role': role
                    })
                if {'artist': name, 'artist_url': img_url} not in artist_data:
                    artist_data.append({
                        'artist': name,
                        'artist_url': img_url
                    })
            except NoSuchElementException:
                continue

        # 다음 버튼이 있는지 확인하고 클릭하여 더 많은 출연진 로드
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'product_casting_nav.swiper-button-next.casting-list-swiper-next')
            if next_button.is_enabled():
                ActionChains(driver).move_to_element(next_button).click(next_button).perform()
                #time.sleep(3)  
            else:
                break
        except NoSuchElementException:
            # 다음 버튼을 찾을 수 없으면 루프 종료
            break
    
    # 출연진 데이터와 아티스트 데이터는 변수에 저장
    print("Cast Data:", cast_data)
    print("Artist Data:", artist_data)
    print("HTML:", main_content_html)
except NoSuchElementException:
    print("'common_container page_detail' 클래스를 가진 요소를 이 페이지에서 찾을 수 없습니다. 클래스 이름이 변경되었거나 요소가 동적으로 로드되었는지 확인하십시오.")

except WebDriverException as e:
    print(f"WebDriver error: {e}")

finally:
    # Closing the driver
    driver.quit()
