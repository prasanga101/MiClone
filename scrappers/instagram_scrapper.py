from scrappers.base_scrapper import BaseScrapper
from config.settings import password
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class InstagramScrapper(BaseScrapper):
    def __init__(self):
        super().__init__()
        self.platform = "instagram"

    def login(self):
        self.driver.get("https://www.instagram.com/")
        time.sleep(3)
        if "accounts/login" not in self.driver.current_url:
            print("Already logged in to Instagram!")
            return
        fb_btn = self.wait_for_element("button[type='button']")
        fb_btn.click()
        time.sleep(5)
        print("Logged in to Instagram via Facebook!")

    def _get_convo_names(self):
        return self.driver.execute_script("""
            const result = [];
            for (const span of document.querySelectorAll('span[title]')) {
                if (!span.title) continue;
                let el = span;
                let skip = false;
                while (el) {
                    if (el.getAttribute && el.getAttribute('aria-haspopup') === 'dialog') {
                        skip = true; break;
                    }
                    if (el.getAttribute && el.getAttribute('role') === 'button') break;
                    el = el.parentElement;
                }
                if (!skip && span.title) result.push(span.title);
            }
            return [...new Set(result)];
        """)

    def _click_convo_by_name(self, name):
        self.driver.execute_script("""
            const name = arguments[0];
            for (const span of document.querySelectorAll('span[title]')) {
                if (span.title !== name) continue;
                let el = span;
                while (el) {
                    if (el.getAttribute && el.getAttribute('role') === 'button') {
                        el.click(); return;
                    }
                    el = el.parentElement;
                }
            }
        """, name)

    def _scroll_inbox(self, amount=400):
        self.driver.execute_script("""
            const pagelet = document.querySelector('[data-pagelet="IGDInboxThreadListScrollableAreaPagelet"]');
            let el = pagelet;
            while (el) {
                const s = window.getComputedStyle(el);
                if ((s.overflowY === 'auto' || s.overflowY === 'scroll') && el.scrollHeight > el.clientHeight) {
                    el.scrollTop += arguments[0];
                    return;
                }
                el = el.parentElement;
            }
            window.scrollBy(0, arguments[0]);
        """, amount)

    def get_convos(self, max_convos=60):
        # Phase 1: scroll inbox and collect names only (no clicking, no reloads)
        self.driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(5)

        all_names = []
        seen_names = set()
        no_new_rounds = 0

        while no_new_rounds < 3 and len(all_names) < max_convos:
            names = self._get_convo_names()
            new_names = [n for n in names if n not in seen_names]

            if not new_names:
                no_new_rounds += 1
            else:
                no_new_rounds = 0
                for n in new_names:
                    seen_names.add(n)
                    all_names.append(n)
                    if len(all_names) >= max_convos:
                        break

            self._scroll_inbox(400)
            time.sleep(1)

        print(f"Collected {len(all_names)} conversation names, now getting URLs...")

        # Phase 2: click each conversation once to get its URL
        all_convos = []
        for i, name in enumerate(all_names):
            self.driver.get("https://www.instagram.com/direct/inbox/")
            time.sleep(4)
            self._scroll_inbox(i * 80)
            time.sleep(1)
            try:
                self._click_convo_by_name(name)
                time.sleep(2)
                url = self.driver.current_url
                if '/direct/t/' in url:
                    all_convos.append({"name": name, "href": url})
                    print(f"  Found: {name}")
            except Exception as e:
                print(f"  Error: {name}: {e}")

        print(f"Found {len(all_convos)} conversations")
        return all_convos

    def _scroll_msg_container(self):
        self.driver.execute_script("""
            // Find anchor element - try role="group" first, then any message-like element
            let anchor = document.querySelector('[role="group"]');
            if (!anchor) {
                anchor = document.querySelector('[data-scope="messages_table"]');
            }

            if (anchor) {
                let el = anchor.parentElement;
                while (el && el !== document.body) {
                    const style = window.getComputedStyle(el);
                    if ((style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                        el.scrollHeight > el.clientHeight) {
                        el.scrollTop -= 600;
                        return;
                    }
                    el = el.parentElement;
                }
            }

            // Fallback: find largest scrollable div on page
            let best = null, bestH = 0;
            for (const div of document.querySelectorAll('div')) {
                const s = window.getComputedStyle(div);
                if ((s.overflowY === 'auto' || s.overflowY === 'scroll') &&
                    div.scrollHeight > div.clientHeight && div.clientHeight > 200) {
                    if (div.clientHeight > bestH) { bestH = div.clientHeight; best = div; }
                }
            }
            if (best) best.scrollTop -= 600;
        """)

    def scrape_msgs(self, convo):
        self.driver.get(convo["href"])
        time.sleep(2)

        seen_keys = set()
        all_messages = []
        no_new_rounds = 0
        scroll_count = 0
        max_scrolls = 150

        while no_new_rounds < 10 and scroll_count < max_scrolls:
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
        print("Monitoring Instagram for new messages...")
        last_seen = {}

        while True:
            try:
                convos = self.get_convos()

                for i, convo in enumerate(convos):
                    self.driver.get(convo["href"])
                    time.sleep(2)

                    msg_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='group']")

                    if not msg_elements:
                        continue

                    last_msg = msg_elements[-1].text.strip()

                    if last_seen.get(i) != last_msg:
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
