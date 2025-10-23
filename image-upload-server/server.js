const express = require('express');
const multer = require('multer');
const path = require('path'); // Needed for resolving file paths
const app = express();
const PORT = 8080;

// --- 1. CONFIGURE MULTER STORAGE ---
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

// ------------------------------------------------------------------
// --- 2. ADD DEFAULT ROUTE (Handles GET /) ---
// This route sends the index.html file when a user navigates to the root URL (http://localhost:3000/)
app.get('/', (req, res) => {
    // __dirname is the absolute path to the directory containing this script.
    res.sendFile(path.join(__dirname, 'index.html'));
});
// ------------------------------------------------------------------

// --- 3. THE UPLOAD ROUTE HANDLER (Handles POST /upload-image) ---
app.post('/upload-image', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file was uploaded.');
    }

    console.log('File uploaded:', req.file);
    
    // Respond to the client
    res.send(`
        <h1>File Upload Success!</h1>
        <p>File saved to server as: <strong>${req.file.filename}</strong></p>
        <p>Original name: ${req.file.originalname}</p>
        <p><a href="/">Go back to upload form</a></p>
    `);
});

// --- 4. START THE SERVER ---
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});