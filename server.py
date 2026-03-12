import json
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MarvelRivalsGMAnalyzer")

# Force the script to look in its own directory for the database
# This prevents crashes when Claude runs it from a background system folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "compiled_database.json")

def load_db() -> dict:
    """Loads the compiled JSON database."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    return {"Maps": {}, "Heroes": {}, "Team_Ups": {}, "last_updated": "Never"}

def get_fuzzy_map(db_maps: dict, map_query: str) -> dict | str:
    """Finds a map in the database using exact or substring matching."""
    if not map_query:
        return "Map data unavailable."
        
    # 1. Try an exact match first
    if map_query in db_maps:
        return db_maps[map_query]
        
    # 2. Clean the query (remove underscores, make lowercase)
    query_clean = map_query.lower().replace("_", " ")
    
    # 3. Search for substrings
    for key, data in db_maps.items():
        key_clean = key.lower().replace("_", " ")
        # If 'yggsgard' is in 'yggsgard yggdrasill path', we have a match!
        if query_clean in key_clean or key_clean in query_clean:
            return data
            
    return f"Map '{map_query}' not found in database."

@mcp.tool()
def analyze_matchup(map_name: str, enemy_team: list[str]) -> str:
    """
    Analyze a 6-stack enemy composition to identify active Team-Ups and map advantages.
    
    Args:
        map_name: The current map (e.g., 'Tokyo_2099_Spider_Islands' or just 'Yggsgard')
        enemy_team: List of up to 6 enemy hero names.
    """
    db = load_db()
    
    analysis = {
        "map_context": get_fuzzy_map(db.get("Maps", {}), map_name),
        "active_synergies": [],
        "enemy_stats": {}
    }
    
    for hero in enemy_team:
        hero_data = db["Heroes"].get(hero, {})
        analysis["enemy_stats"][hero] = hero_data.get("gm_winrate", "N/A")
    
    active_tu_names = set()
    for hero in enemy_team:
        for tu in db["Heroes"].get(hero, {}).get("team_ups", []):
            tu_data = db["Team_Ups"].get(tu)
            if tu_data:
                # Synergy is active if at least 2 required heroes are present
                present_activators = [h for h in tu_data["activators"] if h in enemy_team]
                if len(present_activators) >= 2:
                    active_tu_names.add(tu)
                    
    for tu in active_tu_names:
        analysis["active_synergies"].append({
            "name": tu,
            "mechanic": db["Team_Ups"][tu]["effect"],
            "counter_tactic": db["Team_Ups"][tu]["counter"]
        })
        
    return json.dumps(analysis, indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")