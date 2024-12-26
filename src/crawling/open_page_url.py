import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def get_open_page_url(base_num):
    
    # ChromePtions 객체 생성
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 결과 데이터 저장
    open_page_list = []

    # base_num부터 시작해 max_pages 만큼 반복
    for num in range(base_file_number, 100):
        try:
            open_page_url = f'https://ticket.interpark.com/webzine/paper/TPNoticeView.asp?bbsno=34&pageno=233&stext=&no={num}&groupno={num}&seq=0&KindOfGoods=TICKET&Genre=&sort=WriteDate'
            driver.get(open_page_url)


            try:
                # `open` 클래스 요소 확인
                open_element = driver.find_element(By.CLASS_NAME, "open")
                
                # 날짜 추출
                open_date = open_element.text.split("\n")[1]
                print(f"추출된 날짜: {open_date}")

                # "2024년" 또는 "2025년"이 포함된 경우만 처리
                if "2024년" in open_date or "2025년" in open_date:
                    open_page_list.append(open_page_url)
                    print("데이터를 저장합니다")
            
            except:
                print(f"티켓오픈일이 없어 {num+1}로 넘어갑니다")
                continue
        except:
            print("open_page_url 접속 에러")
      
    return open_page_list



#get_open_page_url(53717,10)
