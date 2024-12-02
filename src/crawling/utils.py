import os
from configparser import ConfigParser

# 현재 파일 경로를 기준으로 절대 경로 반환
def get_path():
    return os.path.dirname(os.path.abspath(__file__))

# offset.ini 파일을 읽고 저장하는 함수
def get_config(path=None):
    config_path = path if path else get_path()
    config = ConfigParser()

    # config 폴더 내 offset.ini 경로 설정
    config_file_path = os.path.join(config_path, "config", "offset.ini")

    # 파일이 존재하는지 확인하고, 없다면 기본값을 설정하여 생성
    if not os.path.exists(config_file_path):
        print(f"offset.ini 파일이 {config_file_path}에 존재하지 않으므로 기본값으로 생성합니다.")
        config['DEFAULT'] = {'offset': '1'}  # 기본 offset 값 설정
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)  # config 폴더가 없다면 생성
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    config.read(config_file_path)
    return config

# get_offset 함수: offset 값 읽기
def get_offset():
    try:
        config = get_config()
        return int(config["DEFAULT"]["offset"])
    except KeyError as e:
        print(f"KeyError: {e} 발생! 설정 파일에서 'offset' 키를 찾을 수 없습니다.")
        print("기본값 1을 사용합니다.")
        return 1

# set_offset 함수: offset 값 저장
def set_offset(offset):
    config = get_config()
    config.set("DEFAULT", "offset", str(offset))
    
    # offset.ini 파일의 경로를 설정
    config_file_path = os.path.join(get_path(), "config", "offset.ini")
    
    print(f"저장 경로: {config_file_path}")  # 저장 경로 출력 (디버깅용)

    # 파일을 열어서 설정 내용을 저장
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    
    print(f"offset 값을 {offset}으로 저장했습니다.")  # 저장 확인 메시지


