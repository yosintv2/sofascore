import requests
import os

def fetch_live_scores():
    url = "https://www.sofascore.com/api/v1/sport/football/events/live"
    # Essential headers to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        events = data.get('events', [])
        
        # Format the scores into a Markdown table
        output = "## ⚽ Live Football Scores\n\n"
        output += "| Match | Score | Status |\n| :--- | :---: | :--- |\n"
        
        for event in events[:15]: # Limit to top 15 matches
            home_team = event['homeTeam']['name']
            away_team = event['awayTeam']['name']
            home_score = event['homeScore'].get('current', 0)
            away_score = event['awayScore'].get('current', 0)
            status = event['status']['description']
            
            output += f"| {home_team} vs {away_team} | {home_score} - {away_score} | {status} |\n"
            
        return output
    except Exception as e:
        return f"Error fetching scores: {e}"

def update_readme(content):
    with open("README.md", "r") as f:
        lines = f.readlines()

    # Look for placeholders in your README to replace content
    new_readme = []
    skip = False
    for line in lines:
        if "" in line:
            new_readme.append(line)
            new_readme.append(content + "\n")
            skip = True
        elif "" in line:
            new_readme.append(line)
            skip = False
        elif not skip:
            new_readme.append(line)

    with open("README.md", "w") as f:
        f.writelines(new_readme)

if __name__ == "__main__":
    scores_md = fetch_live_scores()
    update_readme(scores_md)
