from supabase import create_client
from config.settings import db_url,db_key

def conn():
    """Creates a Supabase client instance"""
    supabase = create_client(db_url, db_key)
    return supabase

if __name__ == "__main__":
    db = conn()
    print("Connected to Supabase successfully!")