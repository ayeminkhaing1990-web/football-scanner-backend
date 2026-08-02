import os
import json
import requests
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ==========================================
# 📊 CONFIDENCE SCORE CALCULATION ALGORITHM
# ==========================================
def calculate_confidence(phase1_pass, phase2_pass, phase3_pass, stats):
    score = 0
    
    # Phase 1 Weight (20%)
    if phase1_pass:
        score += 20
        
    # Phase 2 Weight (35%)
    if phase2_pass:
        score += 35
        
    # Phase 3 Weight (45%)
    if phase3_pass:
        score += 45
        
    # Extra Deductions (အန္တရာယ်ရှိသော Stats များတွေ့ပါက ရမှတ်လျှော့မည်)
    if stats.get("shots", 0) > 4:
        score -= 10
    if stats.get("crosses", 0) > 6:
        score -= 10
        
    return max(0, min(100, score))

# ==========================================
# ⚙️ MAIN SCANNING LOGIC ENGINE
# ==========================================
def process_match(match_data):
    stats = match_data.get("stats", {})
    minute = match_data.get("minute", 0)
    
    # Phase 1 Criteria Check (Pre-match)
    p1_pass = (
        stats.get("xg", 0) <= 1.82 and
        stats.get("corner_avg", 0) <= 8.4 and
        stats.get("sot_avg", 0) <= 5.8 and
        stats.get("ppda", 0) >= 13.1 and
        stats.get("wing_play", "HIGH") == "LOW"
    )
    
    # Pre-match မအောင်ရင် တန်းပြီး SKIP မည်
    if not p1_pass:
        return {"phase": 1, "status": "SKIP", "confidence": 0, "decision": "🔴 SKIP (Pre-match stats high)"}

    # Phase 2 Criteria Check (15' Live)
    p2_pass = False
    if minute >= 15:
        p2_pass = (
            stats.get("corners", 0) <= 1 and
            stats.get("shots", 0) <= 3 and
            stats.get("sot", 0) <= 1 and
            stats.get("dangerous_attacks", 0) <= 27 and
            stats.get("home_score", 0) == 0 and stats.get("away_score", 0) == 0 and
            stats.get("red_cards", 0) == 0
        )
        if not p2_pass and minute < 30:
            return {"phase": 2, "status": "SKIP", "confidence": 15, "decision": "🔴 SKIP (15' High Tempo)"}

    # Phase 3 Criteria Check (30' Live)
    p3_pass = False
    if minute >= 30:
        p3_pass = (
            stats.get("corners", 0) <= 2 and
            stats.get("shots", 0) <= 5 and
            stats.get("sot", 0) <= 2 and
            stats.get("dangerous_attacks", 0) <= 58 and
            stats.get("crosses", 0) <= 7
        )

    # Phase 4 Confidence Calculation
    confidence = calculate_confidence(p1_pass, p2_pass, p3_pass, stats)
    
    # Decision Signal Output
    if confidence >= 85:
        status = "PASS"
        decision = "🟢 STRONG UNDER (Under 8.5, Entry 28'-34')"
    elif confidence >= 70:
        status = "MEDIUM"
        decision = "🟡 MEDIUM (စောင့်ကြည့်ပါ)"
    else:
        status = "SKIP"
        decision = "🔴 SKIP"

    current_phase = 4 if minute >= 30 else (2 if minute >= 15 else 1)
    return {"phase": current_phase, "status": status, "confidence": confidence, "decision": decision}

# ==========================================
# 🚀 EXECUTION & DATABASE UPDATE
# ==========================================
def run_live_scanner():
    # နမူနာ Live Match Data (နောက်ပိုင်းတွင် API / Scraper မှ Auto ဝင်လာမည်)
    matches_to_scan = [
        {
            "match_id": "MATCH_001",
            "home_team": "ABC FC",
            "away_team": "XYZ FC",
            "league": "Premier League",
            "minute": 30,
            "stats": {
                "xg": 1.50, "corner_avg": 7.2, "sot_avg": 4.1, "ppda": 14.5, "wing_play": "LOW",
                "corners": 1, "shots": 3, "sot": 1, "dangerous_attacks": 24,
                "home_score": 0, "away_score": 0, "red_cards": 0, "crosses": 4
            }
        },
        {
            "match_id": "MATCH_002",
            "home_team": "Alpha FC",
            "away_team": "Beta FC",
            "league": "La Liga",
            "minute": 30,
            "stats": {
                "xg": 2.10, "corner_avg": 10.5, "sot_avg": 7.0, "ppda": 9.2, "wing_play": "HIGH",
                "corners": 5, "shots": 8, "sot": 4, "dangerous_attacks": 65,
                "home_score": 1, "away_score": 0, "red_cards": 0, "crosses": 12
            }
        }
    ]

    for match in matches_to_scan:
        result = process_match(match)
        data_payload = {
            "match_id": match["match_id"],
            "home_team": match["home_team"],
            "away_team": match["away_team"],
            "league": match["league"],
            "phase": result["phase"],
            "status": result["status"],
            "confidence": result["confidence"],
            "stats": {**match["stats"], "minute": match["minute"], "decision": result["decision"]}
        }
        
        # Supabase ထဲသို့ Upsert (Auto Update) လုပ်ခြင်း
        supabase.table("matches").upsert(data_payload, on_conflict="match_id").execute()
        print(f"Processed {match['home_team']} vs {match['away_team']}: {result['decision']} ({result['confidence']}%)")

if __name__ == "__main__":
    run_live_scanner()
