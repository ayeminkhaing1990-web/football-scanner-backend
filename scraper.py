import os
import json
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL သို့မဟုတ် SUPABASE_KEY မရှိပါ။")
    exit(1)

supabase: Client = create_client(url, key)

def run_scanner_test():
    sample_match = {
        "match_id": "ABC_XYZ_001",
        "home_team": "ABC FC",
        "away_team": "XYZ FC",
        "league": "Test Premier League",
        "phase": 1,
        "status": "PASS",
        "confidence": 92,
        "stats": {
            "xG": 1.82,
            "corner_avg": 8.4,
            "sot_avg": 5.8,
            "ppda": 13.1,
            "wing_play": "LOW"
        }
    }

    response = supabase.table("matches").upsert(sample_match, on_conflict="match_id").execute()
    print("Data Inserted Successfully:", response.data)

if __name__ == "__main__":
    run_scanner_test()
