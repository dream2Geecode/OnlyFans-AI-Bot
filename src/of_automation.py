import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright


class OFBot:
    def generate_reply(self, message: str, profile: str) -> str:
        load_dotenv()
        self.username = os.getenv("OF_USERNAME")
        self.password = os.getenv("OF_PASSWORD")
        if not self.username or not self.password:
            raise ValueError("OF_USERNAME and OF_PASSWORD must be set in .env")

        # Example logic using message and profile
        reply = f"Replying to '{message}' with profile '{profile}'"
        return reply

    def __init__(self, headless: bool = True):
        if not os.path.exists(".env"):
            raise FileNotFoundError(".env file not found")
        load_dotenv()
        self.username = os.getenv("OF_USERNAME")
        self.password = os.getenv("OF_PASSWORD")
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login(self) -> bool:
        """Log in to OnlyFans using credentials from .env"""
        try:
            if not self.page:
                raise ValueError("Page is not initialized.")
            self.page.goto("https://onlyfans.com")

            # Click accept cookies if present
            accept_cookies = self.page.locator("text=Accept All")
            if accept_cookies.count() > 0:
                accept_cookies.click()

            # Fill login form
            if not self.username or not self.password:
                raise ValueError("Username or password is not set.")
            self.page.fill('input[name="username"]', self.username)
            self.page.fill('input[name="password"]', self.password)
            self.page.click('button[type="submit"]')

            # Wait for login to complete
            self.page.wait_for_selector("div.profile-name", timeout=30000)
            return True
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def send_message(self, user_id: str, message: str) -> bool:
        """Send a message to a specific user"""
        try:
            if not self.page:
                raise ValueError("Page is not initialized.")
            self.page.goto(f"https://onlyfans.com/my/chats/{user_id}")
            self.page.wait_for_selector("div.chat-wrapper")

            # Type and send message
            self.page.fill("textarea.message-input", message)
            self.page.click("button.send-message-button")

            # Verify message was sent
            self.page.wait_for_selector(f'div.message-content:has-text("{message}")')
            return True
        except Exception as e:
            print(f"Failed to send message: {str(e)}")
            return False

    def check_new_messages(self) -> list[str]:
        """Check for new messages and return list of senders"""
        try:
            if not self.page:
                raise ValueError("Page is not initialized.")
            self.page.goto("https://onlyfans.com/my/chats")
            self.page.wait_for_selector("div.chat-item")

            # Get all unread chats
            unread_chats = self.page.locator("div.chat-item.unread")
            senders = []

            for i in range(unread_chats.count()):
                sender = unread_chats.nth(i).locator("div.chat-name").inner_text()
                senders.append(sender)

            return senders
        except Exception as e:
            print(f"Failed to check messages: {str(e)}")
            return []

    def reply_to_all_unread(self, bot: "OFBot", profile: str = "default") -> int:
        """Reply to all unread messages using the bot"""
        senders = self.check_new_messages()
        replied_count = 0

        if not self.page:
            raise ValueError("Page is not initialized.")

        for sender in senders:
            try:
                self.page.goto(f"https://onlyfans.com/my/chats/{sender}")
                self.page.wait_for_selector("div.message-content:not(.outgoing)")

                # Get the latest message from the sender
                messages = self.page.locator("div.message-content:not(.outgoing)")
                latest_message = messages.last.inner_text()

                # Generate reply
                reply = bot.generate_reply(latest_message, profile)
                if reply and self.send_message(sender, reply):
                    replied_count += 1

            except Exception as e:
                print(f"Failed to reply to {sender}: {str(e)}")

        return replied_count
