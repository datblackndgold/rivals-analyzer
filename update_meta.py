import json
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Force the script to write the DB to the same folder as the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "compiled_database.json")

# Static Data: Season 6.5 Map geometry and core mechanics
STATIC_SCHEMA = {
    "Maps": {
        "Tokyo_2099_Spider_Islands": {
            "mode": "Convoy",
            "topography": ["Extreme verticality", "Long sightlines"],
            "favored_archetype": "Dive / Hitscan"
        },
        "Tokyo_2099_Shin_Shibuya": {
            "mode": "Domination",
            "topography": ["Tight urban streets", "Choke points"],
            "favored_archetype": "Brawl / Spam"
        },
        "Yggsgard_Yggdrasill_Path": {
            "mode": "Vanguard",
            "topography": ["Tight corridors", "Environmental kill pits"],
            "favored_archetype": "Brawl / AOE"
        },
        "Yggsgard_Royal_Palace": {
            "mode": "Domination",
            "topography": ["Open courtyards", "Multiple flank routes"],
            "favored_archetype": "Poke / Dive"
        },
        "Wakanda_Birnin_T_Chaka": {
            "mode": "Convoy",
            "topography": ["High ground rotation", "Wide payload paths"],
            "favored_archetype": "Hitscan / Shield comps"
        },
        "Museum_of_Contemplation": {
            "mode": "Vanguard",
            "topography": ["Multi-level exhibits", "Destructible cover"],
            "favored_archetype": "Flex / Mid-range"
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
            "activators": ["Iron_Man", "Hulk", "Doctor_Strange", "The_Thing"],
            "effect": "Iron Man's ultimate and primary fire are infused with Gamma. The Thing gains Gamma Gauntlets.",
            "counter": "Requires Doctor Strange or Luna Snow to 'Shield/Freeze' the affected targets during the channel."
        },
        "Mr_Pools_Interdimensional_Toy_Box": {
            "activators": ["Deadpool", "Jeff_the_Land_Shark", "Elsa_Bloodstone"],
            "effect": "Deadpool drops random buffs and healing items for his team-up partners.",
            "counter": "High burst damage. The buffs provide sustain, so out-damaging the passive healing is key."
        },
        "Rocket_Network": {
            "activators": ["Rocket_Raccoon", "Mister_Fantastic", "Star-Lord"],
            "effect": "Flexible tech sharing, giving armor packs or reduced cooldowns.",
            "counter": "Dive the Rocket early to cut off the network's supply line to the DPS."
        },
        "Metallic_Mutant": {
            "activators": ["Magneto", "Scarlet_Witch"],
            "effect": "Scarlet Witch imbues Magneto's greatsword with Chaos magic for massive cleave damage.",
            "counter": "Kite backwards. The greatsword has limited range; punish them during the recovery animation."
        },
        "Planet_X_Pals": {
            "activators": ["Groot", "Rocket_Raccoon"],
            "effect": "Rocket rides on Groot's shoulder, gaining damage reduction.",
            "counter": "Use AoE damage (like Iron Man or Storm) to hit both simultaneously, or anti-heal Groot."
        }
    }
}

def fetch_live_stats() -> dict:
    """Mock fetch of live GM-tier stats for the Season 6.5 meta."""
    return {
        "Venom": {"role": "Vanguard", "winrate": "52.1%"},
        "Spider-Man": {"role": "Duelist", "winrate": "49.8%"},
        "Peni_Parker": {"role": "Vanguard", "winrate": "50.5%"},
        "Hela": {"role": "Duelist", "winrate": "54.2%"},
        "Thor": {"role": "Vanguard", "winrate": "51.5%"},
        "Loki": {"role": "Strategist", "winrate": "50.1%"},
        "Iron_Man": {"role": "Duelist", "winrate": "48.5%"},
        "Hulk": {"role": "Vanguard", "winrate": "46.2%"},
        "Doctor_Strange": {"role": "Vanguard", "winrate": "49.1%"},
        "The_Thing": {"role": "Vanguard", "winrate": "51.2%"},
        "Deadpool": {"role": "Duelist", "winrate": "52.8%"},
        "Jeff_the_Land_Shark": {"role": "Strategist", "winrate": "51.0%"},
        "Elsa_Bloodstone": {"role": "Duelist", "winrate": "53.4%"},
        "Rocket_Raccoon": {"role": "Strategist", "winrate": "52.3%"},
        "Mister_Fantastic": {"role": "Vanguard", "winrate": "48.9%"},
        "Star-Lord": {"role": "Duelist", "winrate": "47.5%"},
        "Magneto": {"role": "Vanguard", "winrate": "53.1%"},
        "Scarlet_Witch": {"role": "Duelist", "winrate": "50.8%"},
        "Groot": {"role": "Vanguard", "winrate": "49.5%"}
    }

def compile_database():
    """Merge live stats with static map/synergy data."""
    logging.info(f"Starting ETL pipeline for Season 6.5...")
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