import json
import logging
import os
import time
from collections import deque
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from openai import OpenAI


class RateLimiter:
    def __init__(self, max_requests_per_hour):
        self.max_requests = max_requests_per_hour
        self.requests = deque()

    def check_limit(self) -> bool:
        now = time.time()
        while self.requests and now - self.requests[0] > 3600:
            self.requests.popleft()
        return len(self.requests) < self.max_requests

    def record_request(self):
        self.requests.append(time.time())


class SafetyFilter:
    def __init__(self):
        self.blocked_terms = set()  # Add blocked terms as needed

    def is_safe(self, text: str) -> bool:
        text = text.lower()
        return not any(term in text for term in self.blocked_terms)


class OFBot:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.safety_filter = SafetyFilter()
        self.rate_limiter = RateLimiter(int(os.getenv("MAX_REPLIES_PER_HOUR", 50)))
        self.logger = self._setup_logging()

    def _setup_logging(self):
        logger = logging.getLogger("OFBot")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler("data/logs/bot.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def generate_reply(self, message: str, profile_name: str = "default") -> str:
        try:
            if not self.safety_filter.is_safe(message):
                return "I can't respond to that message."

            if not self.rate_limiter.check_limit():
                return "I'm getting too many messages right now. Try again later."

            profile = self._load_profile(profile_name)
            response = self._generate_ai_response(message, profile)

            if self.safety_filter.is_safe(response):
                self.rate_limiter.record_request()
                return response
            return "Sorry, I can't respond to that."

        except Exception as e:
            self.logger.error(f"Error generating reply: {str(e)}")
            return "Something went wrong. Please try again later."

    def _load_profile(self, profile_name: str) -> Dict:
        profile_path = Path("data/creator_profiles/" + profile_name + ".json")
        if not profile_path.exists():
            profile_path = Path("data/creator_profiles/default.json")

        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)
            return json.load(f)

    def _generate_ai_response(self, message: str, profile: Dict) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": profile["system_prompt"]},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
        )
        return (
            response.choices[0].message.content
            or "I don't know how to respond to that."
        )
