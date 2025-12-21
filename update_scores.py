from curl_cffi import requests
import json
import os
from datetime import datetime

def fetch_and_save():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    try:
        # Using chrome120 impersonation to bypass Cloudflare
        response = requests.get(url, impersonate="chrome120", timeout=30)
        
        if response.status_code != 200:
            print(f"Failed with status: {response.status_code}")
            return

        data = response.json()
        events = data.get('events', [])
        
        match_list = []
        for event in events:
            # Get the running clock if available (e.g., 65')
            # 'displayTime' or 'description' usually contains the minute for live matches
            match_minute = event.get('status', {}).get('description', 'Live')
            
            # Convert Unix timestamp to readable HH:mm
            start_ts = event.get('startTimestamp')
            start_time = datetime.fromtimestamp(start_ts).strftime('%H:%M') if start_ts else "N/A"
            
            match_list.append({
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "score": f"{event.get('homeScore', {}).get('current', 0)} - {event.get('awayScore', {}).get('current', 0)}",
                "running_time": match_minute, # Current minute
                "start_time": start_time      # Original kick-off
            })

        # Save to JSON
        output_json = {
            "metadata": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "total_live": len(match_list)
            },
            "matches": match_list
        }

        with open("livescore.json", "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=4)
            
        # Update README table for visual check
        table = "| Kick-off | Match | Score | Minute |\n| :--- | :--- | :---: | :--- |\n"
        for m in match_list[:20]:
            table += f"| {m['start_time']} | {m['home']} vs {m['away']} | **{m['score']}** | {m['running_time']} |\n"
        
        with open("README.md", "w") as f:
            f.write(f"# ⚽ Live Scores\n\n{table}\n\n*Last Update: {output_json['metadata']['last_updated']}*")

        print(f"Updated {len(match_list)} matches.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_save()
