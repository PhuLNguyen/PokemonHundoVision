import requests
import math # Only needed if you plan to plug these into the Base Stat calculation function

def extract_main_series_stats(api_url_or_pokemon_data):
    """
    Fetches a Pokémon's main series base stats from the PokeAPI.

    Args:
        api_url_or_pokemon_data (str or json): 
            str: The URL for the Pokémon's data endpoint (e.g., https://pokeapi.co/api/v2/pokemon/blissey).
            json: The Pokémon data already fetched from the API.

    Returns:
        dict: A dictionary containing the six main series base stats, or None on failure.
    """

    if isinstance(api_url_or_pokemon_data, dict):
        data = api_url_or_pokemon_data
    else:
        try:
            response = requests.get(api_url_or_pokemon_data)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            return None
        data = response.json()
    
    # Initialize a dictionary to store the extracted stats
    pokemon_main_stat = {} 
    
    # The stats are in a list, so we iterate through it
    for stat_entry in data['stats']:
        stat_name = stat_entry['stat']['name']
        base_value = stat_entry['base_stat']
        
        # Mapping API names to the variables used in the previous Base Stat calculation script
        if stat_name == 'hp':
            pokemon_main_stat['hp'] = base_value
        elif stat_name == 'attack':
            pokemon_main_stat['atk'] = base_value
        elif stat_name == 'defense':
            pokemon_main_stat['def'] = base_value
        elif stat_name == 'special-attack':
            pokemon_main_stat['sp_atk'] = base_value
        elif stat_name == 'special-defense':
            pokemon_main_stat['sp_def'] = base_value
        elif stat_name == 'speed':
            pokemon_main_stat['speed'] = base_value
            
    return pokemon_main_stat

def calculate_pogo_base_stats(pokemon_main_stat, cpm_at_level_40):
    """
    Calculates the Base Stats (Attack, Defense, Stamina) for Pokémon GO.
    (This function is replicated from the previous step for context)
    """
    # Initialize dictionary to hold PoGO base stats
    pokemon_go_base_stat = {}

    speed_mod = 1 + (pokemon_main_stat['speed'] - 75) / 500.0
    
    # ATK
    atk_higher = max(pokemon_main_stat['atk'], pokemon_main_stat['sp_atk'])
    atk_lower = min(pokemon_main_stat['atk'], pokemon_main_stat['sp_atk'])
    scaled_atk = round(2 * ((7.0/8.0 * atk_higher) + (1.0/8.0 * atk_lower)))
    base_atk = round(scaled_atk * speed_mod)
    pokemon_go_base_stat['atk'] = base_atk
    
    # DEF
    def_higher = max(pokemon_main_stat['def'], pokemon_main_stat['sp_def'])
    def_lower = min(pokemon_main_stat['def'], pokemon_main_stat['sp_def'])
    scaled_def = round(2 * ((5.0/8.0 * def_higher) + (3.0/8.0 * def_lower)))
    base_def = round(scaled_def * speed_mod)
    pokemon_go_base_stat['def'] = base_def
    
    # STA (HP)
    base_sta = math.floor(1.75 * pokemon_main_stat['hp'] + 50)
    pokemon_go_base_stat['sta'] = base_sta
    
    # Calculate unnerfed max L40 CP (IVs 15/15/15)
    # CP = floor(((BaseATK + IV_A) * sqrt(BaseDEF + IV_D) * sqrt(BaseHP + IV_H) * CPM^2) / 10)
    unnerfed_cp_value = (
        (base_atk + 15) * math.sqrt(base_def + 15) * math.sqrt(base_sta + 15) * cpm_at_level_40**2 
    ) / 10
    unnerfed_max_L40_cp = math.floor(unnerfed_cp_value)
    
    # Determine nerf factor
    nerf_factor = 0.91 if unnerfed_max_L40_cp > 4000 else 1.0

    if nerf_factor < 1.0:
        # Apply nerf to base stats
        pokemon_go_base_stat['atk'] = round(base_atk * nerf_factor)
        pokemon_go_base_stat['def'] = round(base_def * nerf_factor)
        pokemon_go_base_stat['sta'] = round(base_sta * nerf_factor)

    return pokemon_go_base_stat
