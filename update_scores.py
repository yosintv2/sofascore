from curl_cffi import requests
import json
import os
from datetime import datetime

def fetch_and_save():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    try:
        # Using chrome120 impersonation to bypass Cloudflare protection
        response = requests.get(url, impersonate="chrome120", timeout=30)
        
        if response.status_code != 200:
            print(f"Failed with status: {response.status_code}")
            return

        data = response.json()
        events = data.get('events', [])
        
        match_list = []
        for event in events:
            # League and Country info
            tournament = event.get('tournament', {})
            league_name = tournament.get('name', 'Unknown League')
            category = tournament.get('category', {})
            country = category.get('name', 'International')
            
            # Round info (e.g., Round 5 or "Final")
            round_data = event.get('roundInfo', {})
            round_num = round_data.get('round', '')
            round_name = f"Round {round_num}" if round_num else ""
            
            # Start time and Clock
            start_ts = event.get('startTimestamp')
            start_time = datetime.fromtimestamp(start_ts).strftime('%H:%M') if start_ts else "N/A"
            match_minute = event.get('status', {}).get('description', 'Live')
            
            match_list.append({
                "country": country,
                "league": league_name,
                "round": round_name,
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "score": f"{event.get('homeScore', {}).get('current', 0)} - {event.get('awayScore', {}).get('current', 0)}",
                "minute": match_minute,
                "kick_off": start_time
            })

        # Save the full structured JSON
        output_json = {
            "metadata": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "total_matches": len(match_list)
            },
            "matches": match_list
        }

        with open("livescore.json", "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=4)
            
        # Update README with a detailed table
        table = "| Time | League | Round | Match | Score | Min |\n| :--- | :--- | :--- | :--- | :---: | :--- |\n"
        for m in match_list:
            # Grouping by country + league
            league_full = f"{m['country']}: {m['league']}"
            table += f"| {m['kick_off']} | {league_full} | {m['round']} | {m['home']} vs {m['away']} | **{m['score']}** | {m['minute']} |\n"
        
        with open("README.md", "w") as f:
            f.write(f"# ⚽ Live Global Football Scores\n\n{table}\n\n*Last Sync: {output_json['metadata']['last_updated']}*")

        print(f"Successfully processed {len(match_list)} matches.")

    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_and_save()
