from database.supabase_client import conn
from database.queries import insert_convo, insert_init_ts, insert_messages_batch, convo_has_messages
from scrappers.instagram_scrapper import InstagramScrapper
from scrappers.messenger_scrapper import MessengerScrapper

class Collector:
    def __init__(self):
        self.messenger = MessengerScrapper()
        self.instagram = InstagramScrapper()

    def collect_messenger(self):
        print("Starting Messenger collection...")
        
        # record init timestamp
        insert_init_ts("messenger")
        
        # start browser and login
        self.messenger.start_browser(attach=True)
        self.messenger.login()
        
        # get all conversations
        convos = self.messenger.get_convos()
        
        for convo in convos:
            convo_name = convo["name"]
            convo_record = insert_convo("messenger", convo_name)
            convo_id = convo_record["id"]

            if convo_has_messages(convo_id):
                print(f"  Skipping {convo_name} (already scraped)")
                continue

            messages = self.messenger.scrape_msgs(convo)
            inserted = insert_messages_batch(convo_id, "messenger", messages)
            print(f"  Saved {len(inserted)} new messages to DB")
        
        print("Messenger collection done!")
        self.messenger.quit()

    def collect_instagram(self):
        print("Starting Instagram collection...")
        
        insert_init_ts("instagram")
        
        self.instagram.start_browser(attach=True)
        self.instagram.login()
        
        convos = self.instagram.get_convos()
        
        for convo in convos:
            convo_name = convo["name"]
            convo_record = insert_convo("instagram", convo_name)
            convo_id = convo_record["id"]

            # no skip check for instagram - previous runs had broken scrolling
            messages = self.instagram.scrape_msgs(convo)
            inserted = insert_messages_batch(convo_id, "instagram", messages)
            print(f"  Saved {len(inserted)} new messages to DB")
        
        print("Instagram collection done!")
        self.instagram.quit()

    def collect_all(self):
        print("Starting full collection...")
        self.collect_messenger()
        self.collect_instagram()
        print("All collection done!")