import time
from src.of_automation import OFAutomation
from dotenv import load_dotenv

def test_automation():
    # Initialize with visible browser for testing
    of = OFAutomation(headless=False, slow_mo=500)  # slow_mo makes actions visible
    
    try:
        # Test login
        print("Testing login...")
        if not of.login():
            print("❌ Login failed")
            return
        
        print("✅ Login successful")
        time.sleep(3)  # Wait to observe
        
        # Test getting unread messages
        print("\nTesting unread messages...")
        messages = of.get_unread_messages()
        print(f"Found {len(messages)} unread messages")
        if messages:
            print(f"First message content: {messages[0]['content'][:50]}...")
        time.sleep(2)
        
        # Test sending a message (to yourself for testing)
        print("\nTesting message sending...")
        test_message = "🤖 This is an automated test message from your bot!"
        if of.send_message(of.username, test_message):
            print("✅ Message sent successfully")
        else:
            print("❌ Failed to send message")
        time.sleep(3)
        
        # Test liking posts (change to a creator you're subscribed to)
        test_creator = "your_creator_username"  # CHANGE THIS
        print(f"\nTesting liking posts from @{test_creator}...")
        liked_count = of.like_recent_posts(test_creator, 2)
        print(f"Liked {liked_count} posts")
        time.sleep(3)
        
    finally:
        # Clean up
        of.close_browser()
        print("\nTest complete")

if __name__ == "__main__":
    load_dotenv()
    test_automation()
