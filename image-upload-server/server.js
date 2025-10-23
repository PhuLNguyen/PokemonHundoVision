const express = require('express');
const multer = require('multer');
const path = require('path');
const { ImageAnnotatorClient } = require('@google-cloud/vision');
const fs = require('fs');
const app = express();

// -------------------------------------------------------------
// 🌟 READ PORT FROM ENVIRONMENT: Use the value set in the Dockerfile
// -------------------------------------------------------------
const PORT = process.env.PORT; 
if (!PORT) {
    console.error("FATAL ERROR: PORT environment variable not set. Using 8080 as fallback.");
    // This fallback is only for robustness; the ENV in the Dockerfile should prevent it.
    // If you need it to run locally outside of Docker easily, you might want to use:
    // const PORT = process.env.PORT || 8080;
}


// --- 1. CONFIGURE VISION CLIENT ---
const visionClient = new ImageAnnotatorClient();

// --- 2. CONFIGURE MULTER STORAGE ---
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/'); 
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });

// --- VISION API FUNCTION ---
async function detectText(filePath) {
  try {
    const imageBuffer = fs.readFileSync(filePath);
    const [result] = await visionClient.textDetection({
      image: { content: imageBuffer.toString('base64') },
    });
    
    const detections = result.textAnnotations;
    
    if (detections && detections.length > 0) {
      return detections[0].description; 
    }
    return 'No text detected.';

  } catch (error) {
    console.error('ERROR during Cloud Vision API call:', error);
    return `OCR Failed: ${error.message}`;
  }
}

// --- 3. DEFAULT ROUTE ---
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// --- 4. THE UPLOAD ROUTE HANDLER ---
app.post('/upload-image', upload.single('image'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file was uploaded.');
    }

    const imagePath = req.file.path;
    console.log('File uploaded:', imagePath);

    const extractedText = await detectText(imagePath);
    console.log('Extracted Text:', extractedText);
    
    res.send(`
        <h1>File Upload & OCR Success!</h1>
        <p>File saved to server as: <strong>${req.file.filename}</strong></p>
        <h2>Extracted Text (OCR Result):</h2>
        <pre>${extractedText}</pre>
        <p><a href="/">Go back to upload form</a></p>
    `);
});

// --- 5. START THE SERVER ---
app.listen(PORT, () => {
    console.log(`Server running and listening on port ${PORT}`);
});