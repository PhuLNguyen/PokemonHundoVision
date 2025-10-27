import requests
import json

def extract_main_series_stats(api_url):
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