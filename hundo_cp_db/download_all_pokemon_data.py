import requests
import json
import time

def call(api_url):
    """
    Fetches a Pokémon's main series base stats from the PokeAPI.

    Args:
        api_url (str): The URL for the Pokémon's data endpoint (e.g., https://pokeapi.co/api/v2/pokemon/blissey).

    Returns:
        dict: A dictionary containing the six main series base stats, or None on failure.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

    data = response.json()
    return data

if __name__ == "__main__":
    input_pokemon_file = 'pokemon_list.json'
    output_file = '1025_pokemon_go.jsonl'

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
        with open(output_file, 'w') as outfile:
            for pokemon in pokemon_list.get('results'):
                pokemon_data = call(pokemon['url'])
                if pokemon_data is None:
                    print(f"Skipping Pokémon {pokemon['name']} due to API fetch error.")
                    continue
                else:
                    print(f"Processing Pokémon: {pokemon['name']}")
                    json.dump(pokemon_data, outfile)
                    outfile.write('\n')
                    outfile.flush()
                    print(f"Data for {pokemon['name']} successfully written.")
                    time.sleep(0.5)  # To avoid hitting API rate limits
        
        print(f"All Pokemon data successfully processed and written to {output_file}.")
    except IOError as e:
        print(f"Error accessing or writing to file {output_file}: {e}")
        exit(3)