import hashlib
import redis

# Simulated Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_cached_features(user_id):
    value = redis_client.get(f"user:{user_id}:score")
    return {"user_score": value if value else "0"}

def compute_request_features(ip_address):
    ip_hash = hashlib.md5(ip_address.encode()).hexdigest()
    return {"ip_hash": ip_hash[:8]}
