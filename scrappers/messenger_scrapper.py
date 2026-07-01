from scrappers.base_scrapper import BaseScrapper
from config.settings import password
from selenium.webdriver.common.by import By
import time

class MessengerScrapper(BaseScrapper):
    def __init__(self):
        super().__init__()
        self.platform = "messenger"

    def login(self):
        self.driver.get("https://www.messenger.com")
        time.sleep(3)
        if "login" not in self.driver.current_url:
            print("Already logged in to Messenger!")
            return
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
        self.driver.get("https://www.messenger.com")
        time.sleep(5)

        seen_hrefs = set()
        all_convos = []
        no_new_rounds = 0
        scroll_count = 0
        max_scrolls = 40
        max_convos = 100

        while no_new_rounds < 10 and scroll_count < max_scrolls and len(all_convos) < max_convos:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/t/']")
            added = 0
            for el in elements:
                try:
                    href = el.get_attribute("href")
                    if href and href not in seen_hrefs:
                        seen_hrefs.add(href)
                        name = el.text.strip().split("\n")[0]
                        all_convos.append({"name": name, "href": href})
                        added += 1
                except Exception:
                    pass

            if added == 0:
                no_new_rounds += 1
            else:
                no_new_rounds = 0

            if elements:
                self.driver.execute_script("arguments[0].scrollIntoView()", elements[-1])
            scroll_count += 1
            time.sleep(1)

        print(f"Found {len(all_convos)} conversations")
        return all_convos

    def _scroll_msg_container(self):
        self.driver.execute_script("""
            const msg = document.querySelector('div.x1yc453h.x126k92a[dir="auto"]');
            if (msg) {
                let el = msg.parentElement;
                while (el && el !== document.body) {
                    const style = window.getComputedStyle(el);
                    if ((style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                        el.scrollHeight > el.clientHeight) {
                        el.scrollTop -= 600;
                        break;
                    }
                    el = el.parentElement;
                }
            }
        """)

    def scrape_msgs(self, convo):
        self.driver.get(convo["href"])
        time.sleep(8)

        seen_keys = set()
        all_messages = []
        no_new_rounds = 0
        scroll_count = 0
        max_scrolls = 200

        while scroll_count < max_scrolls and no_new_rounds < 10:
            msg_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.x1yc453h.x126k92a[dir='auto']")
            added = 0
            for el in msg_elements:
                try:
                    text = el.text.strip()
                    if not text:
                        continue
                    classes = el.get_attribute("class") or ""
                    is_mine = "xyk4ms5" in classes
                    sender = "me" if is_mine else "other"
                    key = (sender, text[:80])
                    if key not in seen_keys:
                        seen_keys.add(key)
                        all_messages.append({"text": text, "is_mine": is_mine, "sender": sender})
                        added += 1
                except Exception:
                    pass

            if added == 0:
                no_new_rounds += 1
            else:
                no_new_rounds = 0

            self._scroll_msg_container()
            scroll_count += 1
            time.sleep(1.5)

        print(f"Scraped {len(all_messages)} messages")
        return all_messages

    def monitor(self, callback, poll_interval=5):
        print("Monitoring for new messages...")
        last_seen = {}

        while True:
            try:
                convos = self.get_convos()

                for i, convo in enumerate(convos):
                    self.driver.get(convo["href"])
                    time.sleep(2)

                    msg_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-scope='messages_table']")

                    if not msg_elements:
                        continue

                    last_msg = msg_elements[-1].text.strip()
                    aria = msg_elements[-1].get_attribute("aria-label") or ""
                    is_mine = email.lower().split("@")[0] in aria.lower()

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
