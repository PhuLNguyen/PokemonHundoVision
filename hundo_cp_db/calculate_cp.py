import math
import json

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
        HUNDO_CP_DICT[max(10, final_cp)] = str(level)

    return HUNDO_CP_DICT

if __name__ == "__main__":
    index = 0
    CPM_TABLE = load_cpm_table()
    pokemon_go_base_stats_file = open('1025_pokemon_go_base_stats.jsonl', 'r')
    output_hundo_cp_file = open('1025_pokemon_go_hundo_cp.jsonl', 'w')
    pokemon_list = [json.loads(line) for line in pokemon_go_base_stats_file]
    for pokemon in pokemon_list:
        index += 1
        hundo_cp_dict = {}
        hundo_cp_dict["ndex"] = index
        hundo_cp_dict["name"] = pokemon['name']
        hundo_cp_dict = hundo_cp_dict | calculate_hundo_cp_dict(pokemon, 15, CPM_TABLE)
        output_hundo_cp_file.write(json.dumps(hundo_cp_dict) + '\n')
        output_hundo_cp_file.flush()
        print(f"Hundo CP Data for {pokemon['name']} successfully written.")

    pokemon_go_base_stats_file.close()
    output_hundo_cp_file.close()