from typing import List

from src.core.event import Event, EventRepository



class RedisEventRepository(EventRepository):
    
    def __init__(self):
        self.redis = redis.Redis(host=st.secrets.HOST,
                        port=st.secrets.PORT,
                        password=st.secrets.PASSWORD, 
                        decode_responses=True) 