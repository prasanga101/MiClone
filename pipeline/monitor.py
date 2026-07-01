from scrappers.messenger_scrapper import MessengerScrapper
from scrappers.instagram_scrapper import InstagramScrapper
from database.queries import insert_init_ts, check_seen_msg, insert_seen_msg, insert_message
import threading
import time

class Monitor:
    def __init__(self):
        self.messenger = MessengerScrapper()
        self.instagram = InstagramScrapper()

    def handle_new_message(self, platform, message):
        print(f"New message on {platform}: {message}")
        # LLM will plug in here later
        # reply = model.generate_reply(message)

    def start_messenger(self):
        self.messenger.start_browser(attach=True)
        self.messenger.login()
        insert_init_ts("messenger")
        self.messenger.monitor(
            callback=lambda msg: self.handle_new_message("messenger", msg)
        )

    def start_instagram(self):
        self.instagram.start_browser(attach=True)
        self.instagram.login()
        insert_init_ts("instagram")
        self.instagram.monitor(
            callback=lambda msg: self.handle_new_message("instagram", msg)
        )

    def start_all(self):
        print("Starting monitor for all platforms...")
        # run both monitors at the same time using threads
        t1 = threading.Thread(target=self.start_messenger)
        t2 = threading.Thread(target=self.start_instagram)
        t1.start()
        t2.start()
        t1.join()
        t2.join()