import asyncio
import json
import os
from datetime import datetime
from curl_cffi.requests import AsyncSession

SOURCE_NAME = "YoSinTV"

async def get_scorers(session, match_id):
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
                is_home = inc.get('isHome', True)
                side = "H" if is_home else "A"
                scorers.append(f"{player} {time}'({side})")
        return scorers
    except:
        return []

async def fetch_and_save():
    live_url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    async with AsyncSession() as session:
        resp = await session.get(live_url, impersonate="chrome120", timeout=30)
        if resp.status_code != 200: return

        events = resp.json().get('events', [])
        if not events: return

        tasks = []
        matches = []

        for event in events:
            m_id = event['id']
            h_score = event.get('homeScore', {}).get('current', 0)
            a_score = event.get('awayScore', {}).get('current', 0)
            
            # --- EXTRACTING THE ACTUAL CLOCK ---
            # displayTime usually shows "45'" or "90+2'"
            # description is the fallback (shows "HT", "1st half", etc.)
            live_minute = event.get('status', {}).get('displayTime')
            if not live_minute or live_minute == "":
                live_minute = event.get('status', {}).get('description', 'Live')

            match_info = {
                "league": event.get('tournament', {}).get('name', 'Unknown'),
                "country": event.get('tournament', {}).get('category', {}).get('name', ''),
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "score": f"{h_score} - {a_score}",
                "minute": live_minute, # Actual Running Time
                "scorers": []
            }
            matches.append(match_info)
            tasks.append(get_scorers(session, m_id) if (h_score + a_score > 0) else asyncio.sleep(0))

        all_scorers = await asyncio.gather(*tasks)

        for i, s_data in enumerate(all_scorers):
            if isinstance(s_data, list):
                matches[i]["scorers"] = s_data

        # Output JSON
        final_json = {
            "metadata": {"source": SOURCE_NAME, "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")},
            "matches": matches
        }

        with open("livescore.json", "w", encoding="utf-8") as f:
            json.dump(final_json, f, indent=4)

        # Output README Table
        md = "| League | Match | Score | Minute | Scorers |\n| :--- | :--- | :---: | :---: | :--- |\n"
        for m in matches:
            s_list = ", ".join(m['scorers']) if m['scorers'] else "---"
            md += f"| {m['country']} | {m['home']} vs {m['away']} | **{m['score']}** | `{m['minute']}` | {s_list} |\n"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚽ {SOURCE_NAME} Live Dashboard\n\n{md}")

if __name__ == "__main__":
    asyncio.run(fetch_and_save())
