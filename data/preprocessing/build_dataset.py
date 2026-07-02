"""
Rebuild train.jsonl and val.jsonl from Supabase.
Pulls all conversations + messages, builds (other→me) pairs,
shuffles and splits 90/10.

Usage: python -m data.preprocessing.build_dataset
"""
import json
import random
from database.supabase_client import conn

TRAIN_PATH = "data/raw/train.jsonl"
VAL_PATH = "data/raw/val.jsonl"

supabase = conn()

def fetch_conversations():
    result = supabase.table("conversations").select("id,conversation_name,relationship_type").execute()
    return result.data

def fetch_messages(conversation_id):
    all_msgs = []
    page_size = 1000
    offset = 0
    while True:
        result = (
            supabase.table("messages")
            .select("id,sender,text,is_mine")
            .eq("conversation_id", conversation_id)
            .order("id", desc=False)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        all_msgs.extend(result.data)
        if len(result.data) < page_size:
            break
        offset += page_size
    return all_msgs

def collapse_messages(messages):
    """Merge consecutive messages from the same sender into one block."""
    if not messages:
        return []
    blocks = []
    cur_is_mine = messages[0]["is_mine"]
    cur_texts = [(messages[0]["text"] or "").strip()]

    for msg in messages[1:]:
        text = (msg["text"] or "").strip()
        if not text:
            continue
        if msg["is_mine"] == cur_is_mine:
            cur_texts.append(text)
        else:
            combined = "\n".join(t for t in cur_texts if t)
            if combined:
                blocks.append({"is_mine": cur_is_mine, "text": combined})
            cur_is_mine = msg["is_mine"]
            cur_texts = [text]

    combined = "\n".join(t for t in cur_texts if t)
    if combined:
        blocks.append({"is_mine": cur_is_mine, "text": combined})
    return blocks

def build_pairs(convos):
    pairs = []
    skipped_convos = 0

    for convo in convos:
        name = convo["conversation_name"]
        rel = convo.get("relationship_type") or get_relationship(name)

        messages = fetch_messages(convo["id"])
        if not messages:
            skipped_convos += 1
            continue

        blocks = collapse_messages(messages)

        added = 0
        for i in range(len(blocks) - 1):
            cur = blocks[i]
            nxt = blocks[i + 1]

            if cur["is_mine"] or not nxt["is_mine"]:
                continue

            # single-turn: other → me
            pairs.append({
                "text": f"<|user|>\n[{rel}] {cur['text']}<|end|>\n<|assistant|>\n{nxt['text']}<|end|>"
            })
            added += 1

            # multi-turn: include previous (me → other) as context
            if i >= 2 and not blocks[i - 2]["is_mine"] and blocks[i - 1]["is_mine"]:
                prev_other = blocks[i - 2]["text"]
                prev_me = blocks[i - 1]["text"]
                pairs.append({
                    "text": (
                        f"<|user|>\n[{rel}] {prev_other}<|end|>\n"
                        f"<|assistant|>\n{prev_me}<|end|>\n"
                        f"<|user|>\n[{rel}] {cur['text']}<|end|>\n"
                        f"<|assistant|>\n{nxt['text']}<|end|>"
                    )
                })
                added += 1

        print(f"  [{rel}] {name}: {added} pairs")

    print(f"\nSkipped {skipped_convos} empty conversations")
    return pairs

def save_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def main():
    print("Fetching conversations from Supabase...")
    convos = fetch_conversations()
    print(f"Found {len(convos)} conversations\n")

    print("Building training pairs...")
    pairs = build_pairs(convos)

    random.shuffle(pairs)
    split = int(len(pairs) * 0.9)
    train = pairs[:split]
    val = pairs[split:]

    save_jsonl(train, TRAIN_PATH)
    save_jsonl(val, VAL_PATH)

    print(f"\nTotal pairs: {len(pairs)}")
    print(f"Train: {len(train)} → {TRAIN_PATH}")
    print(f"Val:   {len(val)} → {VAL_PATH}")
    print("Done ✓")

if __name__ == "__main__":
    main()
