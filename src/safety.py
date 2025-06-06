from pathlib import Path

from better_profanity import profanity


class SafetyFilter:
    def __init__(self):
        profanity.load_censor_words()
        banned_terms_path = Path("data/banned_terms.txt")
        if banned_terms_path.exists():
            with open(banned_terms_path, "r") as f:
                custom_bad_words = [line.strip() for line in f if line.strip()]
            profanity.add_censor_words(custom_bad_words)

    def is_safe(self, text: str) -> bool:
        if not text:
            return False
        return not profanity.contains_profanity(text)
