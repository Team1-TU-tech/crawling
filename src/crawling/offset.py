import redis

def connect_to_redis():
    return redis.StrictRedis(
        host='redis',  # Redis 컨테이너의 호스트 이름
        port=6379,
        decode_responses=True
    )

def get_last_id_from_redis(ticketlink, default_id=1):
    r = connect_to_redis()
    key = 'ticketlink_last_processed_id'  # 크롤러에 맞는 키 생성
    last_id = r.get(key)
    if last_id is None:
        r.set(key, default_id)  # Redis에 기본값 설정
        return default_id
    return int(last_id)

def update_last_id_in_redis(ticketlink, new_id):
    """
    크롤러에 따라 마지막 처리된 ID를 업데이트하는 함수
    :param crawler_name: 'yes24' 또는 'ticketlink'와 같은 크롤러 이름
    :param new_id: 새로운 ID
    """
    r = connect_to_redis()
    key = 'ticketlink_last_processed_id'  # 크롤러에 맞는 키 생성
    r.set(key, new_id)

    # 오프셋 가져오기 (Redis 사용)
def get_offset():
    return get_last_id_from_redis('ticketlink')  # 'ticketlink_last_processed_id' 키를 사용

# 오프셋 업데이트 (Redis 사용)
def set_offset(new_id):
    update_last_id_in_redis('ticketlink', new_id)  # 'ticketlink_last_processed_id' 키에 새로운 ID 저장

