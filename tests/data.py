import pandas as pd

# 예시 딕셔너리 데이터
data = [{'csoonID': 58399, 'showID': None}, {'csoonID': 58400, 'showID': None}, {'csoonID': 58401, 'showID': '47771'}, {'csoonID': 58402, 'showID': None}, {'csoonID': 58403, 'showID': None}, {'csoonID': 58404, 'showID': None}, {'csoonID': 58406, 'showID': '47762'}, {'csoonID': 58407, 'showID': '47761'}, {'csoonID': 58408, 'showID': '47763'}, {'csoonID': 58409, 'showID': None}, {'csoonID': 58410, 'showID': None}, {'csoonID': 58411, 'showID': '47787'}, {'csoonID': 58412, 'showID': '47768'}, {'csoonID': 58413, 'showID': '47794'}, {'csoonID': 58414, 'showID': None}, {'csoonID': 58415, 'showID': None}, {'csoonID': 58416, 'showID': None}, {'csoonID': 58417, 'showID': None}, {'csoonID': 58418, 'showID': None}, {'csoonID': 58419, 'showID': None}, {'csoonID': 58420, 'showID': None}, {'csoonID': 58421, 'showID': None}, {'csoonID': 58422, 'showID': None}, {'csoonID': 58423, 'showID': None}, {'csoonID': 58424, 'showID': None}, {'csoonID': 58425, 'showID': None}, {'csoonID': 58426, 'showID': None}, {'csoonID': 58427, 'showID': None}, {'csoonID': 58428, 'showID': None}, {'csoonID': 58429, 'showID': None}, {'csoonID': 58430, 'showID': None}, {'csoonID': 58431, 'showID': None}, {'csoonID': 58432, 'showID': None}, {'csoonID': 58433, 'showID': None}, {'csoonID': 58434, 'showID': '47818'}, {'csoonID': 58435, 'showID': '47804'}, {'csoonID': 58436, 'showID': '47863'}, {'csoonID': 58437, 'showID': '47879'}, {'csoonID': 58438, 'showID': None}, {'csoonID': 58439, 'showID': '47803'}, {'csoonID': 58440, 'showID': '47886'}, {'csoonID': 58441, 'showID': '47880'}, {'csoonID': 58442, 'showID': '47867'}, {'csoonID': 58443, 'showID': '47853'}, {'csoonID': 58444, 'showID': None}, {'csoonID': 58445, 'showID': '47820'}, {'csoonID': 58446, 'showID': None}, {'csoonID': 58447, 'showID': None}, {'csoonID': 58448, 'showID': None}, {'csoonID': 58449, 'showID': None}, {'csoonID': 58450, 'showID': None}]

# 딕셔너리를 DataFrame으로 변환
df = pd.DataFrame(data)

# CSV 파일로 저장
df.to_csv('linkLog.csv', index=False, encoding='utf-8-sig')  # 'output.csv'는 원하는 파일 이름으로 변경 가능

print("CSV 파일로 저장이 완료되었습니다!")
