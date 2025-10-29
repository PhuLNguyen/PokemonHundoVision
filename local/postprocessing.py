import re

def extract_cp_and_name(ocr_result):
    """
    Extracts both the Pokémon name and the CP number from the OCR result string.

    Args:
        ocr_result (str): The raw text output from the Vision API 
                          (e.g., "e Dialga CP2337").

    Returns:
        tuple: (pokemon_name (str), combat_power (int)), or (None, None) if not found.
    """
    
    # 1. Clean the OCR result: Remove common non-alphanumeric noise and extra spaces.
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', ocr_result).strip()
    
    # 2. Define the Regular Expression Pattern
    # This pattern captures two groups:
    # Group 1: ([a-zA-Z\s]+?): The Pokémon Name (letters and spaces, non-greedy)
    # Group 2: (\d+): The Combat Power number (one or more digits)
    
    # It looks for: NAME, followed by optional spaces, then 'CP', optional spaces, then the NUMBER.
    match = re.search(r'([a-zA-Z\s]+?)\s*CP\s*(\d+)', cleaned_text, re.IGNORECASE)

    if match:
        # Extract the Name (Group 1)
        pokemon_name = match.group(1).strip()
        
        # Additional cleaning for potential leading/trailing noise in the name
        final_name = re.sub(r'[^a-zA-Z\s]', '', pokemon_name).strip()
        
        # Filter common non-name leading characters (like the 'e' from "e Dialga")
        if len(final_name) > 1 and final_name.lower().startswith('e '):
             final_name = final_name[2:]
             
        # Extract the CP (Group 2) and convert to an integer
        combat_power_str = match.group(2)
        combat_power_int = int(combat_power_str)
        
        return final_name, combat_power_int
    
    # Return failure if the pattern wasn't found
    return None, None
