from scrappers.base_scrapper import BaseScrapper
from config.settings import email,password
import time

class MessengerScrapper(BaseScrapper):
    def __init__(self):
        super().__init__()
        self.platform = "messenger"
        
    def login(self):
        self.driver.get("https://www.messenger.com")
        time.sleep(3)
        
        email_field = self.wait_for_element("input[name='email']")
        email_field.clear()
        email_field.send_keys(email)
        
        pass_field = self.wait_for_element("input[name='pass']")
        pass_field.clear()
        pass_field.send_keys(password)
        self.wait_for_element("button[name='login']").click()
        print("Waiting for 2FA approval on your phone...")
        time.sleep(30)
        print("Logged in to Messenger!")
    
    def get_convos(self):
        time.sleep(2)
        convos = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/t/']")
        print(f"Found {len(convos)} conversations")
        return convos
    
    def scrape_msgs(self, convo):
        convo.click()
        time.sleep(2)
        
        messages = []
        msg_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='row']")
        
        for el in msg_elements:
            try:
                text = el.text.strip()
                if not text:
                    continue
                aria = el.get_attribute("aria-label") or ""
                is_mine = email in aria.lower()
                messages.append({
                    "text": text,
                    "is_mine": is_mine,
                    "sender": "me" if is_mine else "other"
                })
            except Exception as e:
                print(f"Error scraping message: {e}")
                continue
        
        print(f"Scraped {len(messages)} messages")
        return messages
    def monitor(self, callback, poll_interval=5):
        print("Monitoring for new messages...")
        last_seen = {}  # tracks last message per conversation

        while True:
            try:
                convos = self.get_convos()

                for i, convo in enumerate(convos):
                    convo.click()
                    time.sleep(2)

                    msg_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, "[role='row']"
                    )

                    if not msg_elements:
                        continue

                    last_msg = msg_elements[-1].text.strip()
                    aria = msg_elements[-1].get_attribute("aria-label") or ""
                    is_mine = email in aria.lower()

                    # Only process if:
                    # 1. message is not from me
                    # 2. haven't seen it before
                    if not is_mine and last_seen.get(i) != last_msg:
                        last_seen[i] = last_msg
                        print(f"New message in conversation {i+1}: {last_msg}")
                        callback(last_msg)  # send to bot/model

                    else:
                        last_seen[i] = last_msg

                time.sleep(poll_interval)

            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(poll_interval)
                continue