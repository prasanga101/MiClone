from scrappers.base_scrapper import BaseScrapper
from config.settings import email, password
import time

class InstagramScrapper(BaseScrapper):
    def __init__(self):
        super().__init__()
        self.platform = "instagram"

    def login(self):
        self.driver.get("https://www.instagram.com/")
        time.sleep(3)

        # Click "Log in with Facebook" button
        fb_btn = self.wait_for_element("button[type='button']")
        fb_btn.click()
        time.sleep(5)
        print("Logged in to Instagram via Facebook!")

    def get_convos(self):
        self.driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(3)

        convos = self.driver.find_elements(
            By.CSS_SELECTOR, "a[href*='/direct/t/']"
        )
        print(f"Found {len(convos)} conversations")
        return convos

    def scrape_msgs(self, convo):
        convo.click()
        time.sleep(2)

        messages = []
        msg_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "[role='row']"
        )

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
        print("Monitoring Instagram for new messages...")
        last_seen = {}

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

                    if not is_mine and last_seen.get(i) != last_msg:
                        last_seen[i] = last_msg
                        print(f"New message in conversation {i+1}: {last_msg}")
                        callback(last_msg)
                    else:
                        last_seen[i] = last_msg

                time.sleep(poll_interval)

            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(poll_interval)
                continue