from database.supabase_client import conn

supabase = conn()

def insert_convo(platform, conversation_name):
    result = supabase.table("conversations").insert({
        "platform": platform,
        "conversation_name": conversation_name
    }).execute()
    return result.data[0]

def insert_message(conversation_id, platform, sender, text, is_mine):
    result = supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "platform": platform,
        "sender": sender,
        "text": text,
        "is_mine": is_mine
    }).execute()
    return result.data[0]

def insert_init_ts(platform):
    result = supabase.table("init_timestamp").insert({
        "platform": platform
    }).execute()
    return result.data[0]

def insert_seen_msg(message_id):
    result = supabase.table("seen_messages").insert({
        "message_id": message_id
    }).execute()
    return result.data[0]

def check_seen_msg(message_id):
    result = supabase.table("seen_messages").select("*").eq("message_id", message_id).execute()
    return len(result.data) > 0