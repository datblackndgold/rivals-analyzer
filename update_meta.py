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
        },
        "Yggsgard_Yggdrasill_Path": {
            "mode": "Vanguard",
            "topography": ["Tight corridors", "Environmental kill pits"],
            "favored_archetype": "Brawl / AOE"
        }
    },
    "Team_Ups": {
        "Symbiote_Bond": {
            "activators": ["Venom", "Spider-Man", "Peni_Parker"],
            "effect": "Converts incoming damage to explosive AoE retaliation.",
            "counter": "Engage from 15m+ range; use anti-heal to prevent sustain during the burst window."
        },
        "God_of_Mischief": {
            "activators": ["Hela", "Thor", "Loki"],
            "effect": "Hela can resurrect Thor and Loki instantly; Thor gets lightning damage buff.",
            "counter": "Prioritize Hela first. If she is alive, killing Thor or Loki is a wasted cooldown."
        },
        "Gamma_Charge": {
            "activators": ["Iron_Man", "Hulk", "Doctor_Strange"],
            "effect": "Iron Man's ultimate and primary fire are infused with Gamma, dealing massive AOE burn.",
            "counter": "Requires Doctor Strange or Luna Snow to 'Shield/Freeze' the Iron Man during the channel."
        }
    }
}

def fetch_live_stats() -> dict:
    """Mock fetch of live GM-tier stats from a community API."""
    # We added the new heroes here so the ETL pipeline processes them!
    return {
        "Venom": {"role": "Vanguard", "winrate": "52.1%"},
        "Spider-Man": {"role": "Duelist", "winrate": "49.8%"},
        "Hela": {"role": "Duelist", "winrate": "54.2%"},
        "Thor": {"role": "Vanguard", "winrate": "51.5%"},
        "Loki": {"role": "Strategist", "winrate": "50.1%"},
        "Iron_Man": {"role": "Duelist", "winrate": "48.5%"},
        "Hulk": {"role": "Vanguard", "winrate": "46.2%"},
        "Doctor_Strange": {"role": "Vanguard", "winrate": "49.1%"}
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