import pytest
from unittest.mock import MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from crawling.all import all_scrape_data  # 크롤링 함수가 포함된 모듈 임포트

# Mocking the get_link function
def mock_get_link(driver):
    # 테스트용 링크 목록 반환
    return ['http://ticket.yes24.com/Perf/51733']

# Mocking the Chrome WebDriver
@pytest.fixture
def mock_driver():
    # Mocking WebDriver의 기본 동작
    driver = MagicMock()
    
    # WebDriver에서 get() 함수 호출 시 아무 동작도 하지 않도록 설정
    driver.get = MagicMock()

    # 페이지 로딩을 기다리는 WebDriverWait의 동작도 모의 처리
    WebDriverWait(driver, 10).until = MagicMock()

    # driver.page_source가 실제 페이지 소스를 반환하는 것처럼 설정
    driver.page_source = """
        <html>
            <body>
                <div class="renew-content">Test Content</div>
                <div class="renew-content">Another Test Content</div>
            </body>
        </html>
    """
    
    return driver

# Test the all_scrape_data function
def test_all_scrape_data(mock_driver):
    # get_link 함수를 모의 처리
    all_links = mock_get_link(mock_driver)
    
    # 크롤링 함수 실행
    mock_driver.get.return_value = None  # get() 함수 호출 시 아무 동작도 하지 않도록 설정
    mock_driver.page_source = """
        <html>
            <body>
                <div class="renew-content">Test Content</div>
                <div class="renew-content">Another Test Content</div>
            </body>
        </html>
    """
    
    # 실제 크롤링 함수 실행
    all_scraped_data = all_scrape_data()  # 크롤링 함수 호출

    # 크롤링 데이터에 대한 예상값 설정
    expected_data = "Test Content\nAnother Test Content\n"
    
    # assert 문을 사용해 결과를 검증
    assert all_scraped_data == expected_data, f"Expected '{expected_data}', but got '{all_scraped_data}'"

