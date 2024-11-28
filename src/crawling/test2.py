from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Selenium WebDriver 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저 UI 없이 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 접속할 URL
url = "http://ticket.yes24.com/Perf/51671"  # 데이터를 가져올 실제 URL을 입력하세요.
driver.get(url)

# 페이지 로드 시간 대기
time.sleep(5)  # 페이지가 완전히 로드되도록 충분히 대기

# 페이지 소스 가져오기
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
raw_content = soup.find_all(class_="renew-content")
print(raw_content)
