import yaml
import requests
import re
from pathlib import Path

# 🔹 VORGABE des Users (NICHT ändern!)
BASE_URL = "https://github.com/iptv-org/iptv/blob/master/streams"

# 🔹 interne Umwandlung in RAW (technisch notwendig)
RAW_BASE_URL = (
    BASE_URL
    .replace("https://github.com/", "https://raw.githubusercontent.com/")
    .replace("/blob/", "/")
)

def clean_name(name: str) -> str:
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\[.*?\]", "", name)
    name = re.sub(r"\s+HD$", "", name, flags=re.IGNORECASE)
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

md_lines = ["# 📺 Meine IPTV Sender\n"]
m3u_lines = ["#EXTM3U\n"]

for source in config["sources"]:
    country = source["country"]
    wanted_raw = source["channels"]
    wanted = [clean_name(w) for w in wanted_raw]

    # ⚠️ iptv-org nutzt lowercase country codes
    url = f"{RAW_BASE_URL}/{country.lower()}.m3u"
    print(f"Lade {country} → {url}")

    resp = requests.get(url)
    if resp.status_code == 404:
        print(f"⚠️ Land {country} nicht gefunden – übersprungen")
        continue
    resp.raise_for_status()

    channels = parse_m3u(resp.text)

    md_lines.append(f"\n## {country.lower()}\n")

    for w_raw, w in zip(wanted_raw, wanted):
        match = next((c for c in channels if c["name"] == w), None)

        if match:
            # Markdown
            md_lines.append(
                f"- **{match['name']}**  \n  `{match['url']}`"
            )

            # M3U
            m3u_lines.append(match["extinf"])
            m3u_lines.append(match["url"])
        else:
            md_lines.append(f"- ⚠️ {w_raw} *(nicht gefunden)*")

Path("channels.md").write_text("\n".join(md_lines))
Path("channels.m3u").write_text("\n".join(m3u_lines))
