from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time

def extract_performance_data(driver):
    """Extract main performance data such as location, running time, period, rating, and price."""
    data = {
        "location": None,
        "running_time": None,
        "start_date": None,
        "end_date": None,
        "rating": None,
        "price": None,
    }

    try:
        # Extract location
        location_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '장소')]/following-sibling::div"
        location_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, location_xpath)))
        data["location"] = location_element.text.strip()

        # Extract running time
        running_time_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '관람시간')]/following-sibling::div"
        running_time_element = driver.find_element(By.XPATH, running_time_xpath)
        data["running_time"] = running_time_element.text.strip()

        # Extract period
        period_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '기간')]/following-sibling::div"
        period_element = driver.find_element(By.XPATH, period_xpath)
        period = period_element.text.strip()
        if " - " in period:
            data["start_date"], data["end_date"] = [d.strip() for d in period.split(" - ")]
        else:
            data["start_date"] = data["end_date"] = period.strip()

        # Extract rating
        rating_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '관람등급')]/following-sibling::div"
        rating_element = driver.find_element(By.XPATH, rating_xpath)
        data["rating"] = rating_element.text.strip()

        # Extract price
        price_xpath = "//ul[@class='product_info_list type_col2']//span[contains(text(), '가격')]/following-sibling::div/ul[@class='product_info_sublist']/li[@class='product_info_subitem']"
        price_elements = driver.find_elements(By.XPATH, price_xpath)
        prices = [elem.text.strip() for elem in price_elements]
        data["price"] = ", ".join(prices)

    except NoSuchElementException as e:
        print(f"데이터를 찾을 수 없습니다: {e}")
    except TimeoutException as e:
        print(f"시간 초과로 데이터를 가져오지 못했습니다: {e}")

    return data

def extract_cast_data(driver):
    """Extract cast data and their roles."""
    cast_data, artist_data = [], []
    try:
        time.sleep(3)  # Wait for HTML to load
        main_content = driver.find_element(By.CLASS_NAME, 'common_container.page_detail')

        while True:
            cast_list = main_content.find_elements(By.CLASS_NAME, 'product_casting_item')
            for cast in cast_list:
                try:
                    img_url = cast.find_element(By.CLASS_NAME, 'product_casting_imgbox').find_element(By.TAG_NAME, 'img').get_attribute('src')
                    name = cast.find_element(By.CLASS_NAME, 'product_casting_name').text.strip()
                    role = cast.find_element(By.CLASS_NAME, 'product_casting_role').text.strip()

                    # Avoid duplicate entries
                    if {'name': name, 'role': role} not in cast_data:
                        cast_data.append({'name': name, 'role': role})
                    if {'artist': name, 'artist_url': img_url} not in artist_data:
                        artist_data.append({'artist': name, 'artist_url': img_url})
                except NoSuchElementException:
                    continue

            # Check for the "Next" button and click if available
            try:
                next_button = driver.find_element(By.CLASS_NAME, 'product_casting_nav.swiper-button-next.casting-list-swiper-next')
                if next_button.is_enabled():
                    ActionChains(driver).move_to_element(next_button).click(next_button).perform()
                    time.sleep(1)
                else:
                    break
            except NoSuchElementException:
                break
    except NoSuchElementException:
        print("출연진 정보를 찾을 수 없습니다.")

    return cast_data, artist_data

def save_minified_html(driver, output_file="minified_ticketlink.html"):
    """Save the current page's HTML content without extra whitespace."""
    try:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        minified_html = soup.prettify(formatter="minimal").replace("\n", "").strip()

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(minified_html)
        print(f"HTML이 공백 없이 '{output_file}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"HTML 저장 중 오류 발생: {e}")

def main():
    driver = webdriver.Chrome()
    url = "https://www.ticketlink.co.kr/product/52656"
    driver.get(url)

    try:
        # Extract performance data
        performance_data = extract_performance_data(driver)

        # Extract cast data
        cast_data, artist_data = extract_cast_data(driver)

        # Save HTML
        save_minified_html(driver)

        # Print extracted data
        print("공연 데이터:")
        for key, value in performance_data.items():
            print(f"{key}: {value}")
        print("Cast Data:", cast_data)
        print("Artist Data:", artist_data)

    except WebDriverException as e:
        print(f"WebDriver 오류 발생: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()