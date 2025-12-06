import json
import os 
from flask import Flask, request, jsonify, render_template, send_file
from google.cloud import vision, firestore
from postprocessing import extract_cp_and_name

# -------------------------------------------------------------
# Configuration
# Cloud Run automatically injects the PORT environment variable
PORT = int(os.environ.get("PORT", 8080))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Initialize the Firestore client
# It automatically uses the Cloud Run Service Account credentials (ADC).
DATABASE_ID = 'pogo'
COLLECTION_NAME = u'hundodata'
db = firestore.Client(database=DATABASE_ID)
hundodata_collection = db.collection(COLLECTION_NAME)

# Initialize Google Cloud Vision Client
vision_client = vision.ImageAnnotatorClient()

#-------------------------------------------------------------
# Helper Functions
#-------------------------------------------------------------
def allowed_file(filename):
    """Checks if a file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_image(image_file):
    """Performs document text detection (OCR)"""
    content = image_file.read()
    
    image = vision.Image(content=content)
    feature = vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION)
    request = vision.AnnotateImageRequest(
        image=image,
        features=[feature],
    )

    response = vision_client.annotate_image(request=request)
    texts = response.text_annotations
    
    if texts:
        # The first annotation contains the full text detected in the image
        return texts[0].description
    
    return "No text detected."

def init_db():
    data_filename = "./pokemon-data/hundo-data.jsonl"
    documents_to_insert = []

    # Check if the collection exist and has any data
    query = hundodata_collection.limit(1)
    results = query.get()
    if results:
        print(f"Collection {COLLECTION_NAME} exists and has some data!")
        return
    else:
        print(f"Collection {COLLECTION_NAME} not exists nor has any data!")

    print("Open Pokemon data file...")

    try:
        with open(data_filename, "r") as file:
            for line in file:
                line = line.strip()
                document = json.loads(line)
                documents_to_insert.append(document)

        # This is much faster than individual 'add' calls.
        batch = db.batch()

        for document in documents_to_insert:
            # create new document reference
            doc_ref = hundodata_collection.document()
            # add document to the batch
            batch.set(doc_ref, document)

        print("Finished reading file", data_filename, ". Inserting Pokemon data into Firestore...")
        batch.commit()
        print("Finished insertion of", len(documents_to_insert), "Pokemons!")
    except Exception as e:
        print("Unexpected error: ", e)

init_db()
app = Flask(__name__)

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
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if image_file and allowed_file(image_file.filename):
        try:
            name = None
            cp = None
            pokemon_lvl = None

            # Process the image using OCR
            ocr_text = read_image(image_file)

            print(f"Vision API result: {ocr_text}")

            # Extract Pokémon name and CP from the OCR result
            name, cp = extract_cp_and_name(ocr_text)
            name_lowercase = name.lower() if name else name

            print(f"Extracted name and cp: {name}, CP: {cp}")

            # Create the query: Select documents where 'name' equals the pokemon name
            # .limit(1) ensures the query stops after finding the first match
            query = hundodata_collection.where(u'name', u'==', name_lowercase).limit(1)

            # Execute the query
            # The .get() method returns a list of DocumentSnapshot objects
            results = query.get()

            if results:
                # Access the first doc in the list
                doc = results[0]
                print("Docs: ", doc)
                pokemon_hundo_dict = doc.to_dict()
                print("Pokemon dict: ", pokemon_hundo_dict)
                cp = str(cp)
                if cp in pokemon_hundo_dict:
                    pokemon_lvl = pokemon_hundo_dict[cp]       
                    print("Pokemon lvl: ", pokemon_lvl)         

            # Return the detected text as a JSON response
            return jsonify({
                "Vision API result": ocr_text,
                "Extracted Pokémon Name": name,
                "Extracted Combat Power (CP)": cp,
                "HUNDO?": "Yes" if pokemon_lvl else "No",
                "Pokemon Level": pokemon_lvl
            }), 200
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": f"{e}"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400

#-------------------------------------------------------------
# Main entry point when running the server locally
# python3 server.py
#-------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)
