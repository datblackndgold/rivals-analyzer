import json
import logging
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load the hidden variables from the .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# ENVIRONMENT VARIABLES (Now Secure!)
# ==========================================
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ... rest of your code stays exactly the same ...
DATABASE_FILE = os.path.join(BASE_DIR, "compiled_database.json")

# We keep Maps and Team_Ups static for now to ensure the pipeline is stable.
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
        "God_of_Mischief": {
            "activators": ["Hela", "Thor", "Loki"],
            "effect": "Hela can resurrect Thor and Loki instantly.",
            "counter": "Prioritize Hela first. Killing Thor/Loki is a wasted cooldown."
        },
        "Symbiote_Bond": {
            "activators": ["Venom", "Spider-Man", "Peni_Parker"],
            "effect": "Converts incoming damage to explosive AoE retaliation.",
            "counter": "Engage from 15m+ range; use anti-heal."
        }
    }
}

def fetch_notion_heroes() -> dict:
    """Fetches live hero stats directly from the Notion Headless CMS."""
    logging.info("Pinging Notion API...")
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Notion API Error: {response.text}")
        return {}

    data = response.json()
    heroes_dict = {}

    # Notion's JSON is deeply nested. This parses it cleanly.
    for row in data.get("results", []):
        props = row.get("properties", {})
        
        try:
            # Extract Name (Title property)
            name = props.get("Name", {}).get("title", [{}])[0].get("plain_text", "Unknown")
            
            # Extract Role (Select property)
            role_data = props.get("Role", {}).get("select")
            role = role_data.get("name") if role_data else "Unknown"
            
            # Extract Winrate (Rich Text property)
            winrate_data = props.get("Winrate", {}).get("rich_text", [])
            winrate = winrate_data[0].get("plain_text", "N/A") if winrate_data else "N/A"
            
            if name != "Unknown":
                heroes_dict[name] = {"role": role, "winrate": winrate}
                
        except IndexError:
            logging.warning("Skipped a row due to missing data.")
            continue

    logging.info(f"Successfully pulled {len(heroes_dict)} heroes from Notion.")
    return heroes_dict

def compile_database():
    """Merge Notion CMS stats with static map/synergy data."""
    logging.info("Starting ETL pipeline...")
    
    # Hit the Notion API instead of the mock data!
    live_data = fetch_notion_heroes()
    
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