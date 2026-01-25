import yaml
import requests
import re
from pathlib import Path

BASE_URL = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams"

def parse_m3u(m3u_text):
    entries = []
    lines = m3u_text.splitlines()

    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            name = re.search(r",(.+)$", lines[i])
            if name:
                entries.append({
                    "name": name.group(1).strip(),
                    "url": lines[i + 1].strip()
                })
    return entries


config = yaml.safe_load(Path("channels.yml").read_text())
output = ["# 📺 Meine IPTV Sender\n"]

for source in config["sources"]:
    country = source["country"]
    wanted = source["channels"]

    print(f"Lade {country}…")
    m3u = requests.get(f"{BASE_URL}/{country}.m3u").text
    channels = parse_m3u(m3u)

    output.append(f"\n## {country}\n")

    for w in wanted:
        match = next((c for c in channels if c["name"] == w), None)
        if match:
            output.append(f"- **{match['name']}**  \n  `{match['url']}`")
        else:
            output.append(f"- ⚠️ {w} *(nicht gefunden)*")

Path("channels.md").write_text("\n".join(output))
