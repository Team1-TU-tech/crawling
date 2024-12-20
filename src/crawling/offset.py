import os
from configparser import ConfigParser

# offset.ini 파일을 읽고 저장하는 함수
def get_path():
    return os.path.dirname(os.path.abspath(__file__))

def get_config(path=None):
    config_path = path if path else get_path()
    config = ConfigParser()
    config_file_path = os.path.join(config_path, "config", "offset.ini")

    if not os.path.exists(config_file_path):
        print(f"offset.ini 파일이 {config_file_path}에 존재하지 않으므로 기본값으로 생성합니다.")
        config['DEFAULT'] = {'offset': '59908'}
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    config.read(config_file_path)
    return config

def get_offset():
    try:
        config = get_config()
        return int(config["DEFAULT"]["offset"])
    except KeyError as e:
        print(f"KeyError: {e} 발생! 설정 파일에서 'offset' 키를 찾을 수 없습니다.")
        print("기본값 58399을 사용합니다.")
        return 1

def set_offset(offset):
    config = get_config()
    config.set("DEFAULT", "offset", str(offset))
    config_file_path = os.path.join(get_path(), "config", "offset.ini")
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    print(f"offset 값을 {offset}으로 저장했습니다.")