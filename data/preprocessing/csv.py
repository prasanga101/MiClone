import pandas as pd
import json
import random

df = pd.read_csv("/Users/prasangauprety/Documents/MiClone/data/raw/messges.csv")
print(df.head())
print(f"Total rows: {len(df)}")

# build conversation pairs
training_data = []

for convo_name, group in df.groupby('conversation_name'):
    relationship = group['relationship_type'].iloc[0]
    messages = group.reset_index(drop=True)
    
    for i in range(len(messages) - 1):
        current = messages.iloc[i]
        next_msg = messages.iloc[i + 1]
        
        if current['is_mine'] == False and next_msg['is_mine'] == True:
            text_in = str(current['text']).strip()
            text_out = str(next_msg['text']).strip()
            
            if not text_in or not text_out:
                continue
            if text_in == 'nan' or text_out == 'nan':
                continue
            
            training_data.append({
                "text": f"<|user|>\n[{relationship}] {text_in}<|end|>\n<|assistant|>\n{text_out}<|end|>"
            })

print(f"Training pairs: {len(training_data)}")

# split 90/10
random.shuffle(training_data)
split = int(len(training_data) * 0.9)
train = training_data[:split]
val = training_data[split:]

# save
with open('data/raw/train.jsonl', 'w', encoding='utf-8') as f:
    for item in train:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

with open('data/raw/val.jsonl', 'w', encoding='utf-8') as f:
    for item in val:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"Train: {len(train)} | Val: {len(val)}")
print("Ready for fine-tuning! ✅")