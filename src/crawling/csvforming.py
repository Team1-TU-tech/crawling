import csv

# 파일 경로 설정
input_file = 'open_info.csv'  # 원본 CSV 파일
output_file = 'id.csv'        # 추출된 데이터를 저장할 CSV 파일

try:
    # 입력 파일 읽기
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # 헤더 읽기
        
        # 열 인덱스 확인
        if 'csoonID' not in header or 'showID' not in header:
            raise ValueError("'csoonID' 또는 'showID' 열이 없습니다.")
        
        csoonID_index = header.index('csoonID')
        showID_index = header.index('showID')
        
        # 추출 데이터를 저장할 리스트 초기화
        extracted_data = []
        
        for row in reader:
            # showID가 비어있지 않은 경우에만 추출
            if row[showID_index].strip():
                extracted_data.append([row[showID_index], row[csoonID_index]])
    
    # 출력 파일 쓰기
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        # 헤더 쓰기
        writer.writerow(['showID', 'csoonID'])
        # 데이터 쓰기
        writer.writerows(extracted_data)
    
    print(f"추출 완료: {output_file}에 저장되었습니다.")

except Exception as e:
    print(f"오류 발생: {e}")
