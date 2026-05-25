"""Generate demo chat data for SoulLoom demo."""
import json, random
from datetime import datetime, timedelta

stages = [
    ("2024-03-01", "2024-04-15", 80, ["在吗", "好的", "收到", "谢谢"]),
    ("2024-04-16", "2024-06-30", 300, ["哈哈", "笑死", "冲", "约起来"]),
    ("2024-07-01", "2024-08-31", 40, ["嗯", "好的", "行", "改天吧"]),
    ("2024-09-01", "2024-11-15", 250, ["帮忙", "一起", "咱", "没问题"]),
    ("2024-11-16", "2025-01-31", 100, ["好", "嗯", "收到", "下次"]),
]

msgs = []
for i, (start, end, vol, vocab) in enumerate(stages):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    days = (e - s).days
    avg = vol / max(days, 1)
    for d in range(days):
        day = s + timedelta(days=d)
        count = max(0, int(random.gauss(avg, avg * 0.5)))
        for _ in range(count):
            t = day + timedelta(hours=random.randint(8, 23), minutes=random.randint(0, 59))
            m = random.choice(vocab)
            if random.random() < 0.3:
                m += random.choice(["啊", "吧", "嘛", "~", "！"])
            msgs.append({"s": random.choice(["我", "对方"]), "t": t.strftime("%Y-%m-%d %H:%M"), "m": m})

msgs.sort(key=lambda x: x["t"])
output_path = r"C:\Users\ASUS\.claude\skills\soulloom\demo_chat.json"
json.dump(msgs, open(output_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"Generated {len(msgs)} messages")
print(f"Saved to {output_path}")
