from src.bot_core import OFBot
from src.of_automation import OFAutomation
from src.utilities import create_creator_profile

def test_system():
    # Create a test profile
    create_creator_profile("test_creator", {
        "system_prompt": "You are a sexy AI assistant",
        "response_style": "playful"
    })
    
    # Test message generation
    bot = OFBot()
    reply = bot.generate_reply("Hey beautiful", "test_creator")
    print(f"Generated reply: {reply}")
    
    # Test automation (comment out if you don't want browser to launch)
    automator = OFAutomation()
    print("Starting browser automation...")
    automator.run("test_creator")

if __name__ == "__main__":
    test_system()
