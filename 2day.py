import asyncio
import json
import os
from datetime import datetime, timedelta
from curl_cffi.requests import AsyncSession

async def fetch_and_save():
    print("--- Debug Start ---")
    
    # Calculate Date
    target_date = datetime.now() + timedelta(days=2)
    date_str = target_date.strftime('%Y-%m-%d')
    file_name = target_date.strftime('%Y%m%d') + ".json"
    
    print(f"Targeting Date: {date_str}")

    # Ensure Folder exists
    if not os.path.exists('date'):
        print("Folder 'date' doesn't exist. Creating it...")
        os.makedirs('date')
    else:
        print("Folder 'date' already exists.")

    scheduled_url = f"https://www.sofascore.com/api/v1/sport/football/scheduled-events/{date_str}"
    
    async with AsyncSession() as session:
        print(f"Fetching from: {scheduled_url}")
        try:
            resp = await session.get(scheduled_url, impersonate="chrome120", timeout=30)
            print(f"API Response Code: {resp.status_code}")
            
            if resp.status_code != 200:
                print("Error: Could not reach Sofascore. They might be blocking your IP.")
                return

            data = resp.json()
            events = data.get('events', [])
            print(f"Found {len(events)} events.")

            if not events:
                print("No events found for this specific date.")
                return

            matches = []
            for event in events:
                matches.append({
                    "home": event['homeTeam']['name'],
                    "away": event['awayTeam']['name'],
                    "score": f"{event.get('homeScore', {}).get('current', 0)} - {event.get('awayScore', {}).get('current', 0)}"
                })

            final_json = {"matches": matches}
            
            # Save File
            save_path = os.path.join("date", file_name)
            print(f"Attempting to save to: {os.path.abspath(save_path)}")
            
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(final_json, f, indent=4)
            
            print("--- SUCCESS: File Generated! ---")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_save())
