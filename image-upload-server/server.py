import os # We'll use this to read the MONGO_URI from the environment var defined in docker-compose.yaml
from flask import Flask, request, jsonify, render_template, send_file
from pymongo import MongoClient
from google.cloud import vision
from preprocessing import detect_dark_oval_banner
from postprocessing import extract_cp_and_name

# -------------------------------------------------------------
# Configuration
# Cloud Run automatically injects the PORT environment variable
PORT = int(os.environ.get("PORT", 8080))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# --- Get the MongoDB Connection URI from environment variables ---
# This is defined in your docker-compose.yaml as the variable MONGO_URI
# The value will be: 'mongodb://mongodb:27017/pogo'
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/pogo') # Fallback to localhost for local testing

app = Flask(__name__)

# --- Establish the MongoDB connection ---
try:
    client = MongoClient(MONGO_URI)
    # Ping the server to check the connection
    client.admin.command('ping') 
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    # You might want to handle this more gracefully in a production app
    exit(1)

# Initialize Google Cloud Vision Client
vision_client = vision.ImageAnnotatorClient()

#-------------------------------------------------------------
# Helper Functions
#-------------------------------------------------------------
def allowed_file(filename):
    """Checks if a file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_text_from_bytes(image_bytes):
    """Performs document text detection (OCR) on the image bytes."""
    
    image = vision.Image(content=image_bytes)

    # Use DOCUMENT_TEXT_DETECTION for dense, multi-block text
    response = vision_client.document_text_detection(image=image)
    
    if response.full_text_annotation and response.full_text_annotation.text:
        return response.full_text_annotation.text
    return "No text detected."

def find_field_name_by_value(document, target_value):
    """
    Searches a Python dictionary (MongoDB document) for a specific value
    and returns the corresponding key (field name).
    """
    
    # 1. Iterate through the key-value pairs of the dictionary
    for key, value in document.items():
        
        # 2. Skip fields that are not CP values (i.e., 'Ndex' and 'Name')
        # We only want to check fields whose keys are numbers (the levels)
        if key in ['Ndex', 'Name']:
            continue
            
        # 3. Check if the current value matches the target value
        if value == target_value:
            # 4. If they match, return the key (which is the level)
            return key
            
    # 5. Return None if the value is not found in any relevant field
    return None

#-------------------------------------------------------------
# Routes
#-------------------------------------------------------------
@app.route('/', methods=['GET'])
def home():
    """Serves the index.html file."""
    # Flask automatically looks for index.html in the 'templates' folder
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        try:
            banner_img = detect_dark_oval_banner(file)

            # uncomment line below to send image to server
            # also must uncomment block in preprocessing.py
            #return send_file(banner_img, mimetype='image/jpeg')

            # Process the image using OCR
            ocr_text = detect_text_from_bytes(banner_img)

            print(f"Vision API result: {ocr_text}")

            # Extract Pokémon name and CP from the OCR result
            name, cp = extract_cp_and_name(ocr_text)
            name = name.lower() if name else name

            print(f"Extracted Pokemon Name: {name}, CP: {cp}")

            if name and cp:
                # Find the pokemon in the database along with its hundo data
                pokemon_hundo_data = client.pogo.hundodata.find_one(
                    {"Name": name}
                )

                # Find the level corresponding to the extracted CP
                hundo_lvl = find_field_name_by_value(pokemon_hundo_data, cp)

                # Return the detected text as a JSON response
                return jsonify({
                    "Vision API result": ocr_text,
                    "Extracted Pokémon Name": name,
                    "Extracted Combat Power (CP)": cp,
                    "HUNDO?": "Yes" if hundo_lvl else "No",
                    "100% IV Level": hundo_lvl
                }), 200
            else:
                return jsonify({
                    "Vision API result": ocr_text,
                    "error": "Could not extract Pokémon name and CP from the image."
                }), 422
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": f"Internal server error: {e}"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400

#-------------------------------------------------------------
# Main entry point
#-------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)