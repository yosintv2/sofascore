from curl_cffi import requests
import json
import os
from datetime import datetime

def fetch_and_save():
    # YoSinTV Global Live Score Scraper
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    try:
        # Mimic Chrome 120 TLS fingerprint to bypass Cloudflare
        response = requests.get(url, impersonate="chrome120", timeout=30)
        
        if response.status_code != 200:
            print(f"YoSinTV Error: API returned {response.status_code}")
            return

        data = response.json()
        events = data.get('events', [])
        
        match_list = []
        for event in events:
            # --- Extract Deep Metadata ---
            tournament = event.get('tournament', {})
            category = tournament.get('category', {})
            round_info = event.get('roundInfo', {})
            
            # Extract League, Country, and Round
            league_name = tournament.get('name', 'Unknown League')
            country = category.get('name', 'International')
            round_num = round_info.get('round', '')
            round_text = f"Round {round_num}" if round_num else "N/A"
            
            # --- Match Details ---
            home_team = event.get('homeTeam', {}).get('name', 'Home')
            away_team = event.get('awayTeam', {}).get('name', 'Away')
            
            home_score = event.get('homeScore', {}).get('current', 0)
            away_score = event.get('awayScore', {}).get('current', 0)
            
            # Status / Time
            status_desc = event.get('status', {}).get('description', 'Live')
            start_ts = event.get('startTimestamp')
            start_time = datetime.fromtimestamp(start_ts).strftime('%H:%M') if start_ts else "--:--"

            match_list.append({
                "country": country,
                "league": league_name,
                "round": round_text,
                "kick_off": start_time,
                "home_team": home_team,
                "away_team": away_team,
                "score": f"{home_score} - {away_score}",
                "minute": status_desc
            })

        # --- Generate JSON Output ---
        output_json = {
            "metadata": {
                "source": "YoSinTV",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "active_matches": len(match_list)
            },
            "matches": match_list
        }

        # Save the JSON file
        with open("livescore.json", "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=4)
            
        # --- Update README.md (Visual Dashboard) ---
        table = "| Time | Country | League | Round | Match | Score | Min |\n"
        table += "| :--- | :--- | :--- | :--- | :--- | :---: | :--- |\n"
        
        for m in match_list:
            table += f"| {m['kick_off']} | {m['country']} | {m['league']} | {m['round']} | {m['home_team']} vs {m['away_team']} | **{m['score']}** | {m['minute']} |\n"
        
        header = f"# ⚽ Live Football Dashboard\n\n**Powered by: YoSinTV**\n\n"
        footer = f"\n\n*Last Sync: {output_json['metadata']['last_updated']}*"
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(header + table + footer)

        print(f"YoSinTV Sync Complete: {len(match_list)} matches processed.")

    except Exception as e:
        print(f"YoSinTV Critical Failure: {e}")

if __name__ == "__main__":
    fetch_and_save()
