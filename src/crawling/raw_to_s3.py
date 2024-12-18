from open_page import *
from offset import *
from valid_links import *

# 예매링크의 전체 HTML 추출
def extract_detail_html(driver):

    try:
        # 현재 페이지 HTML 가져오기
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # HTML 공백이 너무 많아서 처리
        minified_html = soup.prettify(formatter="minimal").replace("\n", "").strip()
        return minified_html
    
    except Exception as e:
        print(f"HTML 처리 중 오류 발생: {e}")
        return None
    
def extract_html(driver, csoonID, valid_links):

    # HTML 저장할 리스트
    raw_html = []

    csoon_url = f"https://www.ticketlink.co.kr/help/notice/{csoonID}"
    driver.get(csoon_url)
    print(f"페이지 로드 완료: {driver.current_url}")
    wait = WebDriverWait(driver, 20)

    # 오픈예정 페이지 HTML 추출
    try:
        dl_list_view = driver.find_element(By.CLASS_NAME, "list_view").get_attribute("outerHTML")
    except NoSuchElementException:
        print(f"오픈 예정 페이지의 HTML을 찾을 수 없습니다: csoonID={csoonID}")
        dl_list_view = None
    
    detail_html = None 
    ticket_link = None

    try:
        # 예매 링크 추출
        try:
            last_dd = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "th_info"))
            ).find_elements(By.TAG_NAME, "dd")[-1]
            link_element = last_dd.find_element(By.TAG_NAME, "a")
            ticket_link = link_element.get_attribute("href")
        except NoSuchElementException:
            print("상세 예매 링크를 찾을 수 없습니다. 상세 예매 링크는 None으로 설정됩니다.")

        # 예매 링크 존재 여부 확인
        if ticket_link:
            try:
                driver.get(ticket_link)
                print(f"\n*****추가 데이터 추출을 위해 페이지 이동: {ticket_link}*****\n")

                # 상세 페이지 HTML 추출
                detail_html = extract_detail_html(driver)

            except Exception as e:
                print(f"추가적으로 상세 페이지에서 html 수집을 시도했지만 오류가 발생했습니다: {e}\n")
                ticket_link = None

        else:
            print(f"상세 예매 페이지의 HTML을 찾을 수 없습니다: csoonID={csoonID}. \n")

    except Exception as e:
        print(f"공연 정보 추출 중 오류 발생: {e}\n")

    # dl_list_view와 detail_html이 모두 None이 아닐 때만 추가
    if dl_list_view or detail_html:
        raw_html.append({"ID": f"{csoonID}", "HTML": str(dl_list_view) + str(detail_html)})
    else:
        print(f"ID: {csoonID} - ***오류가 있는 페이지*** HTML 데이터가 모두 비어 있어서 저장하지 않습니다.")

    return raw_html

def crawl_html(valid_links):
    driver = initialize_driver()
    raw_html = []  # 수집한 HTML 데이터를 저장할 리스트

    try:
        for link in valid_links:
            csoonID = link['csoonID']
            try:
                print(f"\nopen_page 데이터 수집을 시작합니다: csoonID = {csoonID}")
                raw_html.extend(extract_html(driver, csoonID, valid_links))
            except Exception as e:
                print(f"오류 발생: csoonID = {csoonID}, 오류: {e}")
                continue
    except Exception as e:
        print(f"전체 프로세스 중단 오류: {e}")
    finally:
        driver.quit()
        print("추가 데이터 수집 완료!")

    return raw_html


def main():
    valid_links = collect_valid_links()

    if valid_links:
        raw_html = crawl_html(valid_links)
        print(f"raw_html은 {raw_html} 다음과 같습니다!")
        return raw_html
    else:
        print("수집된 유효한 링크가 없습니다.")
        return []

if __name__ == "__main__":
    main()