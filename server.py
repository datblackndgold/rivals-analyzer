import json
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MarvelRivalsGMAnalyzer")

# Force the script to look in its own directory for the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "compiled_database.json")

def load_db() -> dict:
# ... (keep the rest of your code exactly the same)
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    return {"Maps": {}, "Heroes": {}, "Team_Ups": {}, "last_updated": "Never"}

@mcp.tool()
def analyze_matchup(map_name: str, enemy_team: list[str]) -> str:
    """
    Analyze a 6-stack enemy composition to identify active Team-Ups and map advantages.
    
    Args:
        map_name: The current map (e.g., 'Tokyo_2099_Spider_Islands')
        enemy_team: List of up to 6 enemy hero names.
    """
    db = load_db()
    
    analysis = {
        "map_context": db["Maps"].get(map_name, "Map data unavailable."),
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