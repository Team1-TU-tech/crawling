import redis

def connect_to_redis():
    """
    Redis 서버에 연결하는 함수
    :return: Redis 클라이언트 객체
    """
    try:
        return redis.StrictRedis(
            host='redis',  # Redis 컨테이너의 호스트 이름
            port=6379,
            decode_responses=True
        )
    except redis.ConnectionError as e:
        print(f"Redis 연결 오류: {e}")
        raise

def get_last_id_from_redis(crawler_name, default_id=58410):
    """
    Redis에서 마지막 처리된 ID를 가져오는 함수
    :param crawler_name: 크롤러 이름 (예: 'ticketlink', 'yes24' 등)
    :param default_id: 기본값
    :return: 마지막 처리된 ID
    """
    r = connect_to_redis()
    key = f'{crawler_name}_last_processed_id'  # 크롤러 이름에 맞는 키 생성
    last_id = r.get(key)
    if last_id is None:
        r.set(key, default_id)  # Redis에 기본값 설정
        return default_id
    return int(last_id)

def update_last_id_in_redis(crawler_name, new_id):
    """
    크롤러에 맞는 마지막 처리된 ID를 Redis에 업데이트하는 함수
    :param crawler_name: 'yes24' 또는 'ticketlink'와 같은 크롤러 이름
    :param new_id: 새로운 ID
    """
    r = connect_to_redis()
    key = f'{crawler_name}_last_processed_id'  # 크롤러 이름에 맞는 키 생성
    r.set(key, new_id)
    print(f"마지막 처리된 ID를 Redis에 업데이트했습니다. {crawler_name}: {new_id}")


