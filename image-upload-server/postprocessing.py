import re

def extract_pokemon_name(ocr_result):
    """
    Extracts the Pokemon name from the OCR result string.

    Args:
        ocr_result (str): The raw text output from the Vision API 
                          (e.g., "e Dialga CP2337").

    Returns:
        str: The extracted and cleaned Pokemon name (e.g., "Dialga"), or None if not found.
    """
    
    # 1. Clean the OCR result
    # The OCR result often contains extraneous characters or is slightly misread.
    # We remove common non-alphanumeric noise and extra spaces.
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', ocr_result).strip()
    
    # 2. Define the Regular Expression Pattern
    # This pattern looks for:
    # - (?:CP\s*\d+): A non-capturing group for "CP" followed by optional space and digits.
    # - (?:[^a-zA-Z]|\b): A non-capturing group to match a non-letter or a word boundary 
    #                     (to ensure the name is properly separated from surrounding noise).
    # - ([a-zA-Z]+): The main capturing group for the Pokémon Name (one or more letters).
    
    # A simplified approach is to look for letters followed by 'CP' and numbers.
    match = re.search(r'([a-zA-Z\s]+?)\s*CP\s*\d+', cleaned_text, re.IGNORECASE)

    if match:
        # The name is in the first capturing group
        pokemon_name = match.group(1).strip()
        
        # Additional cleaning for potential leading/trailing noise (like the 'e' or symbols)
        # Re-apply strict filtering to keep only the letters and spaces in the name
        final_name = re.sub(r'[^a-zA-Z\s]', '', pokemon_name).strip()
        
        # Filter common non-name leading characters that might get included (e.g., a standalone 'e')
        if len(final_name) > 1 and final_name.lower().startswith('e '):
             final_name = final_name[2:]
             
        return final_name
    
    # If the CP pattern isn't found, try to assume the whole string (after cleaning) is the name
    return cleaned_text if cleaned_text else None

# --- Run Step 1 Test ---
ocr_result = "e Dialga CP2337"
pokemon_name = extract_pokemon_name(ocr_result)

print("--- Pokémon Name Extraction Result ---")
print(f"Original OCR: '{ocr_result}'")
print(f"Extracted Pokémon Name: '{pokemon_name}'")
print("--------------------------------------")

# Note: This step also prepares the groundwork for extracting the CP, which we'll do next.