import json
import os
from datetime import datetime

FILE_NAME = "answers.json"

def load_data():
    if not os.path.exists(FILE_NAME):
        return {}
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_entry(user_id, answers):
    data = load_data()

    if str(user_id) not in data:
        data[str(user_id)] = []

    data[str(user_id)].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "answers": answers,
        "mood": answers[-1]
    })

    save_data(data)