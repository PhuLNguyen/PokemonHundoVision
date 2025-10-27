from get_main_to_base import extract_main_series_stats, calculate_pogo_base_stats
from calculate_cp import calculate_hundo_cp_dict, load_cpm_table
import json
import time

if __name__ == "__main__":
    index = 0
    input_pokemon_file = 'pokemon_list.json'
    output_hundo_cp_file = '1025_pokemon_go_hundo_cp.jsonl'
    CPM_TABLE = load_cpm_table()

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

    try:
        with open(output_hundo_cp_file, 'w') as outfile:
            for pokemon in pokemon_list.get('results'):
                index += 1
                
                print(f"Processing Pokémon #{index}: {pokemon['name']}")
                pokemon_main_stat = extract_main_series_stats(pokemon['url'])

                # Calculate the Pokémon GO Base Stats using the fetched data
                pokemon_go_base_stat = calculate_pogo_base_stats(pokemon_main_stat)

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
                
        print(f"All Hundo CP data successfully processed and written to {output_hundo_cp_file}.")
    except IOError as e:
        print(f"Error accessing or writing to file {output_hundo_cp_file}: {e}")
        exit(3)