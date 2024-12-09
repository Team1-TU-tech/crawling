import re

def extract_seat_prices(price_str):
    # 정규 표현식: 좌석과 가격을 추출
    pattern = r'([A-Za-z가-힣]+(?:석)?(?:\([^\)]+\))?)\s*[-]?\(?(\d{1,3}(?:,\d{3})*)\s*원\)?|(\d{1,3}(?:,\d{3})*)\s*원'
    
    result = []
    
    # '/'로 구분된 경우 처리
    price_list = price_str.split(' / ')
    
    for price_item in price_list:
        matches = re.findall(pattern, price_item.strip())
        
        if matches:
            for match in matches:
                if match[0] and match[1]:  # 좌석과 가격이 모두 있는 경우
                    seat = match[0].strip()
                    price = int(match[1].replace(",", ""))
                    price = "{:,.0f}".format(price)
                    result.append({'seat': seat, 'price': f'{price}원'})
                elif match[2]:  # 가격만 있는 경우
                    seat = '일반석'
                    price = int(match[2].replace(",", ""))
                    price = "{:,.0f}".format(price)
                    result.append({'seat': seat, 'price': f'{price}원'})

    if not result:
        return price_list
    
    return result
# 예시 테스트
prices_list = [
    'R석 66,000원 / S석 55,000원 / 시야제한석 25,000원',
    '30,000원',
    'R석 60,000원',
    'VIP-100,000 / R-80,000 / S-60,000',
    'P석(500,000원) R석(400,000원) S석(300,000원) A석(200,000원)',
    '전석 20,000원 (비지정석)',
    'VIP석(1층) 66,000원 / S석(2층) 44,000원',
    '일반 25,000원 / 학생 20,000원'
]

# 결과 출력
for price in prices_list:
    print(extract_seat_prices(price))
