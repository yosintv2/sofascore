import asyncio 
import json
import os
from datetime import datetime, timedelta
from curl_cffi.requests import AsyncSession

SOURCE_NAME = "YoSinTV"

async def get_scorers(session, match_id):
    # Scheduled matches usually don't have scorers yet, 
    # but we keep this for consistency or finished games.
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/incidents"
    try:
        res = await session.get(url, impersonate="chrome120", timeout=10)
        if res.status_code != 200: return []
        incidents = res.json().get('incidents', [])
        scorers = []
        for inc in incidents:
            if inc.get('incidentType') == 'goal':
                player = inc.get('player', {}).get('name', 'Unknown')
                time = inc.get('time', '?')
                side = "H" if inc.get('isHome', True) else "A"
                scorers.append(f"{player} {time}'({side})")
        return scorers
    except:
        return []

async def fetch_and_save():
    # 1. Calculate the date +2 days from today
    target_date = datetime.now() + timedelta(days=2)
    date_str = target_date.strftime('%Y-%m-%d')  # Format: YYYY-MM-DD for URL
    file_name = target_date.strftime('%Y%m%d') + ".json"  # Format: YYYYMMDD.json
    
    # 2. Ensure the 'date' folder exists
    if not os.path.exists('date'):
        os.makedirs('date')

    # 3. Construct the scheduled events URL
    scheduled_url = f"https://www.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}"
    
    async with AsyncSession() as session:
        resp = await session.get(scheduled_url, impersonate="chrome120", timeout=30)
        if resp.status_code != 200: 
            print(f"Failed to fetch data for {date_str}")
            return

        events = resp.json().get('events', [])
        if not events: 
            print(f"No events found for {date_str}")
            return

        tasks = []
        matches = []

        for event in events:
            m_id = event['id']
            h_score = event.get('homeScore', {}).get('current', 0)
            a_score = event.get('awayScore', {}).get('current', 0)
            
            start_ts = event.get('startTimestamp')
            exact_start = datetime.fromtimestamp(start_ts).strftime('%H:%M') if start_ts else "N/A"

            match_info = {
                "start_time": exact_start,
                "league": event.get('tournament', {}).get('name', 'Unknown'),
                "country": event.get('tournament', {}).get('category', {}).get('name', ''),
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "score": f"{h_score} - {a_score}",
                "status": event.get('status', {}).get('description', 'Scheduled'),
                "scorers": []
            }
            matches.append(match_info)
            # Only fetch scorers if the game has goals (unlikely for future games, but good for safety)
            tasks.append(get_scorers(session, m_id) if (h_score + a_score > 0) else asyncio.sleep(0))

        all_scorers = await asyncio.gather(*tasks)

        for i, s_data in enumerate(all_scorers):
            if isinstance(s_data, list):
                matches[i]["scorers"] = s_data

        # 4. Prepare Final JSON
        final_json = {
            "metadata": {
                "source": SOURCE_NAME, 
                "target_date": date_str,
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            },
            "matches": matches
        }

        # 5. Save to date/YYYYMMDD.json
        save_path = os.path.join("date", file_name)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(final_json, f, indent=4)
        
        print(f"Success! Saved {len(matches)} matches to {save_path}")

if __name__ == "__main__":
    asyncio.run(fetch_and_save())
