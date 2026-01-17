import redis

# Initialize Redis connection (local instance on default port 6379)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def check_redis_connection():
    """Test Redis connection"""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False
