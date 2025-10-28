import math
import json
from get_main_to_base import extract_main_series_stats, calculate_pogo_base_stats

# Load the Combat Power Modifier dictionary from a JSON file 
def load_cpm_table():
    try:
        filename = 'cpm.json'
        with open(filename, 'r') as file:
            cpm_data = json.load(file)
        print(f"JSON file successfully loaded {filename}.")
        return cpm_data
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON. Check the file format.")

def calculate_hundo_cp_dict(pokemon_go_base_stat, IV, CPM_TABLE):
    """
    Calculates the Combat Power (CP) of a Pokémon.

    Args:
        pokemon_go_base_stat (dict): A dictionary containing the Pokémon's base stats in Pokémon GO.
        IV (int): The Individual Value for Attack, Defense, and Stamina (default is 15 for a "hundo" Pokémon).

    Returns:
        dict: Max CP per level.
    """
    MIN_LEVEL = 1
    MAX_LEVEL = 50
    HUNDO_CP_DICT = {}

    for level in range(MIN_LEVEL, MAX_LEVEL + 1):
        cpm = CPM_TABLE.get(str(level))
    
        # Main CP Calculation Formula:
        # CP = floor(((ATK_base + IV_ATK) * sqrt(DEF_base + IV_DEF) * sqrt(HP_base + IV_HP) * CPM^2) / 10)
        
        cp_value = ((pokemon_go_base_stat['atk'] + IV) * math.sqrt(pokemon_go_base_stat['def'] + IV) * math.sqrt(pokemon_go_base_stat['sta'] + IV) * cpm**2) / 10
        final_cp = math.floor(cp_value)
        
        # Minimum CP Check: If CP is less than 10, it's set to 10.
        HUNDO_CP_DICT[str(level) ] = max(10, final_cp)

    return HUNDO_CP_DICT
