from curl_cffi import requests
import json
import os
from datetime import datetime

def fetch_and_save():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    # We use impersonate="chrome120" to mimic a real browser's TLS signature
    try:
        response = requests.get(url, impersonate="chrome120", timeout=30)
        
        if response.status_code != 200:
            print(f"Failed with status: {response.status_code}")
            return

        data = response.json()
        events = data.get('events', [])
        
        match_list = []
        for event in events:
            match_list.append({
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "score": f"{event.get('homeScore', {}).get('current', 0)}-{event.get('awayScore', {}).get('current', 0)}",
                "status": event['status']['description']
            })

        # Save to JSON
        output_json = {
            "metadata": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "count": len(match_list)
            },
            "matches": match_list
        }

        with open("livescore.json", "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=4)
            
        print(f"Successfully saved {len(match_list)} matches.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    fetch_and_save()
