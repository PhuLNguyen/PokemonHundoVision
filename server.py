import json
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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# --- Get the MongoDB Connection URI from environment variables ---
MONGODB_URI = os.environ.get("MONGODB_URI")

app = Flask(__name__)

# --- Establish the MongoDB connection ---
try:
    db = MongoClient(MONGODB_URI)
except Exception as e:
    print("Error connecting to MongoDB: ", e)
    # You might want to handle this more gracefully in a production app

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

def init_db():
    data_filename = "hundo-data.jsonl"
    documents_to_insert = []

    print("Open Pokemon data file...")

    try:
        with open(data_filename, "r") as file:
            for line in file:
                line = line.strip()
                document = json.loads(line)
                documents_to_insert.append(document)
        print("Finished reading file", data_filename, ". Inserting data into Firestore (MongoDB)...")
        db.hundodata.insert_many(documents_to_insert)
        print("Finished insertion of", len(documents_to_insert), "Pokemons!")
    except Exception as e:
        print("Unexpected error: ", e)

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
                pokemon_hundo_data = db.hundodata.find_one({"name": name})

                pokemon_lvl = None

                if pokemon_hundo_data:
                    pokemon_lvl = pokemon_hundo_data.get(str(cp))

                # Return the detected text as a JSON response
                return jsonify({
                    "Vision API result": ocr_text,
                    "Extracted Pokémon Name": name,
                    "Extracted Combat Power (CP)": cp,
                    "HUNDO?": "Yes" if pokemon_lvl else "No",
                    "100% IV Level": pokemon_lvl
                }), 200
            else:
                return jsonify({
                    "Vision API result": ocr_text,
                    "error": "Could not extract Pokémon name and CP from the image."
                }), 422
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": f"{e}"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400

#-------------------------------------------------------------
# Main entry point
#-------------------------------------------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=PORT)
