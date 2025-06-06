import json
from pathlib import Path


def create_creator_profile(name: str, system_prompt: str, response_style: str):
    profile = {"system_prompt": system_prompt, "response_style": response_style}

    profile_path = Path(f"data/creator_profiles/{name}.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
