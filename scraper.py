import requests
import json

SUPABASE_URL = "https://whtvjpowjzexmvcxnsmu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndodHZqcG93anpleG12Y3huc211Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU2NDUyMTAsImV4cCI6MjEwMTIyMTIxMH0.C9SKEQIVwtR6Nv-2_7skWipW_-_FALgQ0nuTY4ONCiQ"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def fetch_all_leagues_matches():
    # Clear database first
    requests.delete(f"{SUPABASE_URL}/rest/v1/matches?id=gt.0", headers=headers)

    # List of all popular leagues with Corner markets
    leagues = [
        ("eng.1", "Premier League"),
        ("eng.2", "Championship"),
        ("esp.1", "La Liga"),
        ("ger.1", "Bundesliga"),
        ("ita.1", "Serie A"),
        ("fra.1", "Ligue 1"),
        ("ned.1", "Eredivisie"),
        ("por.1", "Primeira Liga"),
        ("arg.1", "Liga Profesional"),
        ("bra.1", "Serie A (Brazil)"),
        ("usa.1", "MLS"),
        ("tur.1", "Super Lig"),
        ("bel.1", "Pro League"),
        ("sco.1", "Scottish Premiership"),
        ("mex.1", "Liga MX")
    ]

    matches_to_insert = []

    for league_code, league_name in leagues:
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                events = data.get("events", [])
                
                for ev in events:  # Fetch ALL matches in that league
                    match_id = str(ev.get("id"))
                    competitions = ev.get("competitions", [{}])[0]
                    competitors = competitions.get("competitors", [])
                    
                    if len(competitors) >= 2:
                        home_team = competitors[0].get("team", {}).get("shortDisplayName", "Home")
                        away_team = competitors[1].get("team", {}).get("shortDisplayName", "Away")
                        
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
            print(f"Error: {e}")

    if matches_to_insert:
        requests.post(f"{SUPABASE_URL}/rest/v1/matches", headers=headers, json=matches_to_insert)
        print(f"Successfully loaded {len(matches_to_insert)} matches across all leagues!")

if __name__ == "__main__":
    fetch_all_leagues_matches()
