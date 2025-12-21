import asyncio
import json
import os
from datetime import datetime
from curl_cffi.requests import AsyncSession

# YoSinTV Global Live Score Scraper - Unlimited Goal Scorers
SOURCE_NAME = "YoSinTV"

async def get_scorers(session, match_id):
    """Fetch goal scorers for a specific match ID."""
    url = f"https://api.sofascore.com/api/v1/event/{match_id}/incidents"
    try:
        # We use a shorter timeout for individual match lookups
        res = await session.get(url, impersonate="chrome120", timeout=10)
        if res.status_code != 200:
            return []
        
        incidents = res.json().get('incidents', [])
        scorers = []
        for inc in incidents:
            if inc.get('incidentType') == 'goal':
                player = inc.get('player', {}).get('name', 'Unknown Player')
                time = inc.get('time', '?')
                # Check for home or away goal to better attribute it if needed
                is_home = inc.get('isHome', True)
                side = "H" if is_home else "A"
                scorers.append(f"{player} {time}' ({side})")
        return scorers
    except:
        return []

async def fetch_and_save():
    live_url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    
    async with AsyncSession() as session:
        # 1. Fetch all live matches
        resp = await session.get(live_url, impersonate="chrome120", timeout=30)
        if resp.status_code != 200:
            print(f"YoSinTV Error: {resp.status_code}")
            return

        events = resp.json().get('events', [])
        if not events:
            print("No live matches found.")
            return

        # 2. Prepare tasks for ALL matches with goals
        tasks = []
        match_data_placeholders = []

        for event in events:
            m_id = event['id']
            h_score = event.get('homeScore', {}).get('current', 0)
            a_score = event.get('awayScore', {}).get('current', 0)
            
            # Basic match info
            match_info = {
                "id": m_id,
                "league": event.get('tournament', {}).get('name', 'Unknown'),
                "country": event.get('tournament', {}).get('category', {}).get('name', ''),
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "score": f"{h_score} - {a_score}",
                "minute": event.get('status', {}).get('description', 'Live'),
                "scorers": []
            }
            
            match_data_placeholders.append(match_info)
            
            # If goals exist, add to async queue
            if h_score > 0 or a_score > 0:
                tasks.append(get_scorers(session, m_id))
            else:
                tasks.append(asyncio.sleep(0)) # Dummy task for 0-0 games to keep index alignment

        # 3. Execute all requests concurrently
        all_scorers = await asyncio.gather(*tasks)

        # 4. Map scorers back to their matches
        for idx, scorers in enumerate(all_scorers):
            if scorers != 0: # Ignore our dummy sleeps
                match_data_placeholders[idx]["scorers"] = scorers

        # 5. Save JSON
        final_output = {
            "metadata": {
                "source": SOURCE_NAME,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "total_matches": len(match_data_placeholders)
            },
            "matches": match_data_placeholders
        }

        with open("livescore.json", "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=4)

        # 6. Update README Dashboard
        md_table = "| League | Match | Score | Scorers |\n| :--- | :--- | :---: | :--- |\n"
        for m in match_data_placeholders:
            scorer_str = ", ".join(m['scorers']) if m['scorers'] else "---"
            md_table += f"| {m['country']}: {m['league']} | {m['home']} vs {m['away']} | **{m['score']}** | {scorer_str} |\n"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚽ YoSinTV Live Scores (Full Details)\n\n{md_table}\n\n*Updated: {final_output['metadata']['last_updated']}*")

if __name__ == "__main__":
    asyncio.run(fetch_and_save())
