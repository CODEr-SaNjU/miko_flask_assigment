import time
from flask import jsonify,request
import config

cache = config.cache
# initialize rate limiting variables
RATE_LIMIT = 1
RATE_PERIOD = 60


# define a decorator to check if the rate limit has been exceeded
def rate_limited(func):
    def wrapper(*args, **kwargs):
        ip_address = request.remote_addr
        key = f"ratelimit:{request.path}"
        count = cache.get(key)
        if count is None:
            cache.set(key, 1, ex=RATE_PERIOD)
        elif int(count) >= RATE_LIMIT:
            return jsonify({"message": "Rate limit exceeded. Try again in 1 minute."}), 429
        else:
            # increment the request count and set the new TTL
            cache.incr(key)
            cache.expire(key, RATE_PERIOD)
        # call the decorated function
        return func(*args, **kwargs)
    wrapper.__name__=func.__name__
    return wrapper



# authentication decorator
def auth_required(func):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == 'username' and auth.password == 'password'):
            return jsonify({'message': 'Authentication failed'}), 401
        return func(*args, **kwargs)
    
    decorated.__name__ = func.__name__
    return decorated