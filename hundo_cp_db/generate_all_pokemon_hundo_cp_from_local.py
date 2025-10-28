from get_main_to_base import extract_main_series_stats, calculate_pogo_base_stats
from calculate_cp import calculate_hundo_cp_dict, load_cpm_table
import json
import time

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
            print(f"Processing Pokémon #{index}: {pokemon.forms[0]['name']}")
            
            pokemon_main_stat = extract_main_series_stats(pokemon)
            pokemon_main_stat["name"] = pokemon.forms[0]['name']
            output_main_stats_filename.write(json.dumps(pokemon_main_stat) + '\n')
            output_main_stats_filename.flush()
            
            pokemon_go_base_stat = calculate_pogo_base_stats(pokemon_main_stat)
            pokemon_go_base_stat["name"] = pokemon.forms[0]['name']
            output_go_base_stats_filename.write(json.dumps(pokemon_go_base_stat) + '\n')
            output_go_base_stats_filename.flush()
            
            hundo_cp_dict = {}
            hundo_cp_dict["ndex"] = index
            hundo_cp_dict["name"] = pokemon.forms[0]['name']
            hundo_cp_dict = hundo_cp_dict | calculate_hundo_cp_dict(pokemon_go_base_stat, 15, CPM_TABLE)
            output_hundo_cp_filename.write(json.dumps(hundo_cp_dict) + '\n')
            output_hundo_cp_filename.flush()
            print(f"Hundo CP data for {pokemon.forms[0]['name']} successfully written.")

        input_pokemon_file.close()
        output_main_stats_filename.close()
        output_go_base_stats_filename.close()	
        output_hundo_cp_filename.close()
    except FileNotFoundError:
        print(f"Error: The file {input_pokemon_filename} was not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Could not decode JSON. Check the file format.")
        exit(2)
    except IOError as e:
        print(f"Error accessing or writing to file {output_hundo_cp_filename}: {e}")
        exit(3)

"""
                hundo_cp_dict = {}
                hundo_cp_dict["Ndex"] = index
                hundo_cp_dict["Name"] = pokemon['name']
                hundo_cp_dict = hundo_cp_dict | calculate_hundo_cp_dict(pokemon_go_base_stat, 15, CPM_TABLE)
                
                # Write the dictionary immediately and append a newline for JSON Lines format
                json.dump(hundo_cp_dict, outfile)
                outfile.write('\n')
                # Flush the write buffer to the disk immediately (optional, but safer)
                outfile.flush()
                
                print(f"Hundo CP data for {pokemon['name']} successfully written.")

                time.sleep(1)  # To avoid hitting API rate limits
                
        print(f"All Hundo CP data successfully processed and written to {output_hundo_cp_filename}.")
"""    

