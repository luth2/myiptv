import yaml
import requests
import re
from pathlib import Path

BASE_URL = "https://github.com/iptv-org/iptv/blob/master/streams"

def clean_name(name: str) -> str:
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\[.*?\]", "", name)
    return name.strip()

def parse_m3u(text: str):
    entries = []
    lines = text.splitlines()

    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            raw_name = re.search(r",(.+)$", lines[i]).group(1).strip()
            entries.append({
                "raw_name": raw_name,
                "name": clean_name(raw_name),
                "extinf": lines[i],
                "url": lines[i + 1].strip()
            })
    return entries


config = yaml.safe_load(Path("channels.yml").read_text())

md = ["# 📺 Meine IPTV Sender\n"]
m3u = ["#EXTM3U\n"]

for source in config["sources"]:
    country = source["country"]
    wanted = source["channels"]

    print(f"Lade {country}…")
    resp = requests.get(f"{BASE_URL}/{country}.m3u")
    resp.raise_for_status()

    channels = parse_m3u(resp.text)

    md.append(f"\n## {country}\n")

    for w in wanted:
        match = next((c for c in channels if c["name"] == w), None)

        if match:
            # Markdown
            md.append(f"- **{match['name']}**  \n  `{match['url']}`")

            # M3U
            m3u.append(match["extinf"])
            m3u.append(match["url"])
        else:
            md.append(f"- ⚠️ {w} *(nicht gefunden)*")

Path("channels.md").write_text("\n".join(md))
Path("channels.m3u").write_text("\n".join(m3u))
