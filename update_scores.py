import requests
import json
import os
from datetime import datetime

def fetch_and_save():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.sofascore.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return

        data = response.json()
        events = data.get('events', [])

        # 1. Create livescore.json
        json_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "matches": []
        }

        for event in events:
            json_data["matches"].append({
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "score": f"{event.get('homeScore', {}).get('current', 0)} - {event.get('awayScore', {}).get('current', 0)}",
                "status": event['status']['description']
            })

        with open("livescore.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)

        # 2. Update README.md (Visual check)
        table = "| Match | Score | Status |\n| :--- | :---: | :--- |\n"
        for m in json_data["matches"][:15]:
            table += f"| {m['home']} vs {m['away']} | **{m['score']}** | {m['status']} |\n"
        
        with open("README.md", "w") as f:
            f.write(f"# Live Scores\n\n{table}\n\n*Updated: {json_data['last_updated']}*")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    fetch_and_save()
