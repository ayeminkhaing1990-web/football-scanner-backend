import requests
import json

# Supabase Credentials
SUPABASE_URL = "https://whtvjpowjzexmvcxnsmu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndodHZqcG93anpleG12Y3huc211Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU2NDUyMTAsImV4cCI6MjEwMTIyMTIxMH0.C9SKEQIVwtR6Nv-2_7skWipW_-_FALgQ0nuTY4ONCiQ"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def update_live_matches():
    print("Clearing old test matches from Supabase...")
    # Clean up old records
    requests.delete(f"{SUPABASE_URL}/rest/v1/matches?id=gt.0", headers=headers)

    # Leagues to fetch: Premier League, La Liga, Bundesliga, Serie A
    leagues = [
        ("eng.1", "Premier League"),
        ("esp.1", "La Liga"),
        ("ger.1", "Bundesliga"),
        ("ita.1", "Serie A")
    ]

    matches_to_insert = []

    print("Fetching live/upcoming real matches from ESPN API...")
    for league_code, league_name in leagues:
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                events = data.get("events", [])
                
                for ev in events[:2]:  # Take top 2 matches per league
                    match_id = str(ev.get("id"))
                    competitions = ev.get("competitions", [{}])[0]
                    competitors = competitions.get("competitors", [])
                    
                    if len(competitors) >= 2:
                        home_team = competitors[0].get("team", {}).get("shortDisplayName", "Home Team")
                        away_team = competitors[1].get("team", {}).get("shortDisplayName", "Away Team")
                        
                        match_item = {
                            "match_id": match_id,
                            "home_team": home_team,
                            "away_team": away_team,
                            "league": league_name,
                            "phase": 4,
                            "confidence": 92,
                            "status": "PASS",
                            "stats": {
                                "decision": "🟢 STRONG UNDER (Under 8.5, Entry 28'-34')",
                                "corner_avg": 7.4,
                                "sot_avg": 4.2
                            }
                        }
                        matches_to_insert.append(match_item)
        except Exception as e:
            print(f"Error fetching {league_name}: {e}")

    if matches_to_insert:
        print(f"Inserting {len(matches_to_insert)} real matches into Supabase...")
        res = requests.post(f"{SUPABASE_URL}/rest/v1/matches", headers=headers, json=matches_to_insert)
        print("Database Update Result:", res.status_code)
    else:
        print("No active matches fetched.")

if __name__ == "__main__":
    update_live_matches()
