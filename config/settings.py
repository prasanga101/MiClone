from dotenv import load_dotenv
load_dotenv()
import os
email = os.getenv("MESSENGER_EMAIL")
password = os.getenv("MESSENGER_PASSWORD")
db_url = os.getenv("SUPABASE_URL")
db_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")