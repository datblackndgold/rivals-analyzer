import json
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_FILE = "compiled_database.json"

# Static Data: Map geometry and core mechanics that don't change often
STATIC_SCHEMA = {
    "Maps": {
        "Tokyo_2099_Spider_Islands": {
            "mode": "Convoy",
            "topography": ["Extreme verticality", "Long sightlines"],
            "favored_archetype": "Dive / Hitscan"
        }
    },
    "Team_Ups": {
        "Symbiote_Bond": {
            "activators": ["Venom", "Spider-Man", "Peni_Parker"],
            "effect": "Converts incoming damage to explosive AoE retaliation.",
            "counter": "Attack from outside spike burst range; prioritize anti-heal."
        }
    }
}

def fetch_live_stats() -> dict:
    """Mock fetch of live GM-tier stats from a community API."""
    # In a real scenario, this hits mrapi.org or tracker.gg
    return {
        "Venom": {"role": "Vanguard", "winrate": "52.1%"},
        "Spider-Man": {"role": "Duelist", "winrate": "49.8%"}
    }

def compile_database():
    """Merge live stats with static map/synergy data."""
    logging.info("Starting ETL pipeline...")
    live_data = fetch_live_stats()
    
    final_db = STATIC_SCHEMA.copy()
    final_db["Heroes"] = {}
    final_db["last_updated"] = datetime.now().isoformat()
    
    for hero, stats in live_data.items():
        active_team_ups = [
            tu_name for tu_name, tu_data in STATIC_SCHEMA["Team_Ups"].items() 
            if hero in tu_data["activators"]
        ]
        
        final_db["Heroes"][hero] = {
            "role": stats.get("role", "Unknown"),
            "gm_winrate": stats.get("winrate", "N/A"),
            "team_ups": active_team_ups
        }
        
    with open(DATABASE_FILE, "w") as f:
        json.dump(final_db, f, indent=4)
        
    logging.info(f"Database compiled and saved to {DATABASE_FILE}")

if __name__ == "__main__":
    compile_database()