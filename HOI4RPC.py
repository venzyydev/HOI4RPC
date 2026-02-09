import time
import re
from pathlib import Path
from pypresence import Presence

CLIENT_ID = "PUT YOUR ID HERE"
SAVE_DIR = Path.home() / "Documents/Paradox Interactive/Hearts of Iron IV/save games"
HEADER_BYTES = 8192

def newest_save():
    saves = list(SAVE_DIR.glob("*.hoi4"))
    return max(saves, key=lambda f: f.stat().st_mtime) if saves else None

def read_header(path):
    with open(path, "rb") as f:
        return f.read(HEADER_BYTES).decode("utf-8", errors="ignore")

def find(patterns, text):
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return None

rpc = Presence(CLIENT_ID)
rpc.connect()
print("HOI4 RPC running")

last_state = {}

while True:
    save = newest_save()
    if not save:
        time.sleep(10)
        continue

    header = read_header(save)

    tag = find([r'player="([A-Z]{3})"'], header)
    ideology = find([
        r'ruling_party="?([a-z_]+)"?',
        r'ideology="?([a-z_]+)"?'
    ], header)
    date = find([
        r'date="?(\d+\.\d+\.\d+(?:\.\d+)?)"?'
    ], header)

    current = {
        "tag": tag,
        "ideology": ideology,
        "date": date
    }

    if current != last_state and tag:
        print("Updating RPC:", current)

        rpc.update(
            details=f"{tag} • {ideology or 'Unknown'}",
            state=f"Date {date or '????'}",
            large_image=tag.lower(),
            large_text="Hearts of Iron IV"
        )

        last_state = current

    time.sleep(10)
