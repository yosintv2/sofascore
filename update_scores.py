from curl_cffi import requests
import json
from datetime import datetime

def get_goal_scorers(match_id):
    # This fetches the specific events (goals, cards) for one match
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/incidents"
    try:
        res = requests.get(url, impersonate="chrome120", timeout=10)
        if res.status_code != 200: return []
        
        incidents = res.json().get('incidents', [])
        scorers = []
        for inc in incidents:
            if inc.get('incidentType') == 'goal':
                player = inc.get('player', {}).get('name', 'Unknown')
                minute = inc.get('time')
                scorers.append(f"{player} ({minute}')")
        return scorers
    except:
        return []

def fetch_and_save():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    try:
        response = requests.get(url, impersonate="chrome120", timeout=30)
        if response.status_code != 200: return

        events = response.json().get('events', [])
        match_list = []
        
        for event in events[:10]: # Limiting to 10 matches to avoid being blocked for too many requests
            m_id = event['id']
            home_s = event.get('homeScore', {}).get('current', 0)
            away_s = event.get('awayScore', {}).get('current', 0)
            
            # Only fetch scorers if a goal has been scored
            goal_details = []
            if home_s > 0 or away_s > 0:
                goal_details = get_goal_scorers(m_id)

            match_list.append({
                "league": event.get('tournament', {}).get('name'),
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "score": f"{home_s} - {away_s}",
                "scorers": goal_details,
                "minute": event.get('status', {}).get('description')
            })

        # Save Output
        output = {"metadata": {"source": "YoSinTV", "updated": str(datetime.now())}, "matches": match_list}
        with open("livescore.json", "w") as f:
            json.dump(output, f, indent=4)
            
    except Exception as e:
        print(f"YoSinTV Error: {e}")

if __name__ == "__main__":
    fetch_and_save()
