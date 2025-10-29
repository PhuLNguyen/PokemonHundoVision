from get_main_to_base import extract_main_series_stats, calculate_pogo_base_stats
from calculate_cp import calculate_hundo_cp_dict, load_cpm_table
import json

if __name__ == "__main__":
    index = 0
    input_pokemon_filename = '1025_pokemon_main.jsonl'
    output_main_stats_filename = '1025_pokemon_main_stats.jsonl'
    output_go_base_stats_filename = '1025_pokemon_go_base_stats.jsonl'
    output_hundo_cp_filename = '1025_pokemon_go_hundo_cp.jsonl'
    CPM_TABLE = load_cpm_table()

    try:
        input_pokemon_file = open(input_pokemon_filename, 'r')
        output_main_stats_file = open(output_main_stats_filename, 'w')
        output_go_base_stats_file = open(output_go_base_stats_filename, 'w')
        output_hundo_cp_file = open(output_hundo_cp_filename, 'w')
        
        pokemon_list = [json.loads(line) for line in input_pokemon_file]
        print(f"Successfully loaded {input_pokemon_filename}.")
        
        for pokemon in pokemon_list:
            index += 1
            print(f"Processing Pokémon #{index}: {pokemon['forms'][0]['name']}")
            
            pokemon_main_stat = extract_main_series_stats(pokemon)
            pokemon_main_stat["name"] = pokemon['forms'][0]['name']
            output_main_stats_file.write(json.dumps(pokemon_main_stat) + '\n')
            output_main_stats_file.flush()
            
            pokemon_go_base_stat = calculate_pogo_base_stats(pokemon_main_stat, CPM_TABLE.get('40'))
            pokemon_go_base_stat["name"] = pokemon['forms'][0]['name']
            output_go_base_stats_file.write(json.dumps(pokemon_go_base_stat) + '\n')
            output_go_base_stats_file.flush()
            
            hundo_cp_dict = {}
            hundo_cp_dict["ndex"] = index
            hundo_cp_dict["name"] = pokemon['forms'][0]['name']
            hundo_cp_dict = hundo_cp_dict | calculate_hundo_cp_dict(pokemon_go_base_stat, 15, CPM_TABLE)
            output_hundo_cp_file.write(json.dumps(hundo_cp_dict) + '\n')
            output_hundo_cp_file.flush()
            print(f"Hundo CP data for {pokemon['forms'][0]['name']} successfully written.")

        input_pokemon_file.close()
        output_main_stats_file.close()
        output_go_base_stats_file.close()	
        output_hundo_cp_file.close()
    except FileNotFoundError:
        print(f"Error: The file {input_pokemon_filename} was not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Could not decode JSON. Check the file format.")
        exit(2)
    except IOError as e:
        print(f"Error accessing or writing to file {output_hundo_cp_filename}: {e}")
        exit(3)
