from database.supabase_client import conn

supabase = conn()

def insert_convo(platform, conversation_name):
    existing = supabase.table("conversations").select("*").eq("platform", platform).eq("conversation_name", conversation_name).execute()
    if existing.data:
        return existing.data[0]
    result = supabase.table("conversations").insert({
        "platform": platform,
        "conversation_name": conversation_name
    }).execute()
    return result.data[0]

def insert_message(conversation_id, platform, sender, text, is_mine):
    existing = supabase.table("messages").select("*").eq("conversation_id", conversation_id).eq("sender", sender).eq("text", text).execute()
    if existing.data:
        return existing.data[0]
    result = supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "platform": platform,
        "sender": sender,
        "text": text,
        "is_mine": is_mine
    }).execute()
    return result.data[0]

def convo_has_messages(conversation_id):
    result = supabase.table("messages").select("id").eq("conversation_id", conversation_id).limit(1).execute()
    return len(result.data) > 0

def insert_messages_batch(conversation_id, platform, messages):
    if not messages:
        return []
    existing = supabase.table("messages").select("sender,text").eq("conversation_id", conversation_id).execute()
    existing_keys = {(r["sender"], r["text"]) for r in existing.data}
    new_msgs = [
        {"conversation_id": conversation_id, "platform": platform, "sender": m["sender"], "text": m["text"], "is_mine": m["is_mine"]}
        for m in messages
        if (m["sender"], m["text"]) not in existing_keys
    ]
    if not new_msgs:
        return []
    result = supabase.table("messages").insert(new_msgs).execute()
    return result.data

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