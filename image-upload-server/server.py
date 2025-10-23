import os
import io
from flask import Flask, request, jsonify
from google.cloud import vision

# -------------------------------------------------------------
# Configuration
# Cloud Run automatically injects the PORT environment variable
PORT = int(os.environ.get("PORT", 8080))
UPLOAD_FOLDER = 'uploads' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# -------------------------------------------------------------

# Initialize Google Cloud Vision Client
# The client automatically uses Application Default Credentials (ADC)
# which is the recommended method for Cloud Run/GCP environments.
vision_client = vision.ImageAnnotatorClient()

def allowed_file(filename):
    """Checks if a file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_text_from_bytes(image_bytes):
    """Performs document text detection (OCR) on the image bytes."""
    
    # Create a Vision Image object from the file bytes
    image = vision.Image(content=image_bytes)

    # Use DOCUMENT_TEXT_DETECTION for dense, multi-block text (like a document)
    response = vision_client.document_text_detection(image=image)
    
    # The first text annotation contains the full text
    if response.full_text_annotation and response.full_text_annotation.text:
        return response.full_text_annotation.text
    return "No text detected."

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file part is present in the request
    if 'image' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['image']
    
    # Check if a filename was submitted
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Check if the file is allowed
    if file and allowed_file(file.filename):
        try:
            # 1. Read the file into memory (in-memory file upload)
            # This is generally faster and better for ephemeral environments like Cloud Run
            # since it avoids writing to the temporary filesystem.
            image_bytes = file.read()
            
            # 2. Process the image using OCR
            ocr_text = detect_text_from_bytes(image_bytes)

            # 3. Return the detected text as a JSON response
            return jsonify({
                "message": "File uploaded and processed successfully",
                "ocr_result": ocr_text
            }), 200

        except Exception as e:
            # General exception handler for API errors, etc.
            print(f"An error occurred: {e}")
            return jsonify({"error": f"Internal server error: {e}"}), 500
    
    else:
        return jsonify({"error": "File type not allowed"}), 400

# Optional: Basic health check or root route
@app.route('/', methods=['GET'])
def home():
    return "OCR Service is running on port " + str(PORT), 200

if __name__ == '__main__':
    # Flask will listen on 0.0.0.0 (all interfaces) and the port defined by Cloud Run.
    app.run(debug=True, host='0.0.0.0', port=PORT)