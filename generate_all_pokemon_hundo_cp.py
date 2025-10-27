from get_main_to_base import extract_main_series_stats, calculate_pogo_base_stats
from calculate_cp import calculate_hundo_cp_dict
import json
import time

if __name__ == "__main__":
    input_pokemon_file = 'pokemon_list.json'
    output_hundo_cp_file = '1025_pokemon_go_hundo_cp.json'

    try:
        with open(input_pokemon_file, 'r') as file:
            pokemon_list = json.load(file)
        print(f"JSON file successfully loaded {input_pokemon_file}.")
    except FileNotFoundError:
        print(f"Error: The file {input_pokemon_file} was not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Could not decode JSON. Check the file format.")
        exit(2)

    all_pokemon_go_hundo_list = []
    index = 0

    for pokemon in pokemon_list.get('results'):
        index += 1
		
        print(f"Processing Pokémon #{index}: {pokemon['name']}")
        pokemon_main_stat = extract_main_series_stats(pokemon['url'])

    	# Calculate the Pokémon GO Base Stats using the fetched data
        pokemon_go_base_stat = calculate_pogo_base_stats(pokemon_main_stat)

        hundo_cp_dict = {}
        hundo_cp_dict["Ndex"] = index
        hundo_cp_dict["Name"] = pokemon['name']
        hundo_cp_dict = hundo_cp_dict | calculate_hundo_cp_dict(pokemon_go_base_stat, IV=15)
   	 	
        all_pokemon_go_hundo_list.append(hundo_cp_dict)
        
        time.sleep(1)  # To avoid hitting API rate limits

    try:
        with open(output_hundo_cp_file, 'w') as outfile:
            json.dump(all_pokemon_go_hundo_list, outfile, indent=4)
        print(f"Hundo CP data successfully written to {output_hundo_cp_file}.")
    except IOError as e:
        print(f"Error writing to file {output_hundo_cp_file}: {e}")