import redis

def connect_to_redis():
    return redis.StrictRedis(
        host='redis',  # Redis 컨테이너의 호스트 이름
        port=6379,
        decode_responses=True
    )

def get_last_id_from_redis():
    r = connect_to_redis()
    last_id = r.get('last_processed_id')
    return int(last_id) if last_id else 1

def update_last_id_in_redis(new_id):
    r = connect_to_redis()
    r.set('last_processed_id', new_id)

