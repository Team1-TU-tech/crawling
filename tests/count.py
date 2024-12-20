import pandas as pd

# CSV 파일 불러오기
input_file = 'linkLog.csv'  # 원본 CSV 파일 경로
data = pd.read_csv(input_file)

# showID가 있는 데이터와 없는 데이터 분류
showID_present = data[data['showID'].notna()]  # showID가 있는 데이터
showID_absent = data[data['showID'].isna()]    # showID가 없는 데이터

# 결과를 CSV로 저장
# showID_present.to_csv('showID_present.csv', index=False, encoding='utf-8-sig')  # showID가 있는 데이터
# showID_absent.to_csv('showID_absent.csv', index=False, encoding='utf-8-sig')    # showID가 없는 데이터

# 결과 출력
print(f"showID가 있는 데이터: {len(showID_present)}개")
print(f"showID가 없는 데이터: {len(showID_absent)}개")
print("분류된 데이터가 showID_present.csv와 showID_absent.csv로 저장되었습니다!")
