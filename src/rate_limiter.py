from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_per_hour: int = 50):
        self.max_requests = max_per_hour
        self.request_times = []
        
    def check_limit(self) -> bool:
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        self.request_times = [t for t in self.request_times if t > hour_ago]
        return len(self.request_times) < self.max_requests
        
    def record_request(self):
        self.request_times.append(datetime.now())
