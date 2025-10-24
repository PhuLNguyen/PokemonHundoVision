import os
from flask import Flask, request, jsonify, render_template
from google.cloud import vision

# -------------------------------------------------------------
# Configuration
# Cloud Run automatically injects the PORT environment variable
PORT = int(os.environ.get("PORT", 8080))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)

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
            # Read the file into memory
            image_bytes = file.read()
            
            # Process the image using OCR
            ocr_text = detect_text_from_bytes(image_bytes)

            # Return the detected text as a JSON response
            return jsonify({
                "ocr_result": ocr_text
            }), 200

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