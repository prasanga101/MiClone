import json
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from database.queries import insert_convo, insert_messages_batch

YOUR_NAME = "Prasanga Uprety"

SKIP_PHRASES = {
    "started a video chat",
    "started an audio call",
    "missed a video chat",
    "missed an audio call",
    "Liked a message",
    "Reacted",
    "sent an attachment",
}

def get_relationship(title):
    title_lower = title.lower()
    if any(x in title_lower for x in ["purnikaa", "mayalu"]):
        return "lover"
    elif any(x in title_lower for x in ["srija", "grishma", "siblings"]):
        return "sister"
    return "friend"

def parse_folder(folder_path):
    all_messages = []
    json_files = sorted(glob.glob(os.path.join(folder_path, "message_*.json")))

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        title = data.get("title", "Unknown")
        for msg in data.get("messages", []):
            content = msg.get("content", "")
            if not content or any(p in content for p in SKIP_PHRASES):
                continue
            sender = msg.get("sender_name", "")
            all_messages.append({
                "title": title,
                "sender": "me" if sender == YOUR_NAME else "other",
                "text": content,
                "is_mine": sender == YOUR_NAME,
            })

    return all_messages

def process_convo(folder_path, platform):
    messages = parse_folder(folder_path)
    if not messages:
        return None, 0

    title = messages[0]["title"]
    relationship = get_relationship(title)

    convo = insert_convo(platform, title)
    if not convo:
        return None, 0

    inserted = insert_messages_batch(convo["id"], platform, messages)
    return f"  [{relationship}] {title}: {len(messages)} messages ({len(inserted)} new)", len(messages)

def parse_all(inbox_path, platform):
    print(f"Parsing {platform} messages from {inbox_path}")

    folders = [
        os.path.join(inbox_path, d)
        for d in os.listdir(inbox_path)
        if os.path.isdir(os.path.join(inbox_path, d))
    ]

    total = 0
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_convo, f, platform): f for f in folders}
        for future in as_completed(futures):
            try:
                label, count = future.result()
                if label:
                    print(label)
                    total += count
            except Exception as e:
                print(f"  Error processing {futures[future]}: {e}")

    print(f"\nTotal {platform} messages inserted: {total}")

if __name__ == "__main__":
    parse_all(
        "/Users/prasangauprety/Downloads/your_instagram_activity/messages/inbox",
        "instagram"
    )
    parse_all(
        "/Users/prasangauprety/Downloads/your_instagram_activity/messages/message_requests",
        "instagram"
    )
