const express = require('express');
const multer = require('multer');
const path = require('path');
const app = express();
const PORT = 3000;

// --- 1. CONFIGURE MULTER STORAGE ---
const storage = multer.diskStorage({
    // Sets the destination folder for uploads (must exist)
    destination: (req, file, cb) => {
        cb(null, 'uploads/'); 
    },
    // Creates a unique filename (timestamp + original extension)
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

// Initialize Multer with the storage configuration
const upload = multer({ storage: storage });

// Middleware to serve your HTML file (optional, assuming your HTML is in a 'public' folder)
// If you run the HTML directly in the browser, you don't need this line.
// app.use(express.static('public'));

// --- 2. THE UPLOAD ROUTE HANDLER ---
// The path here MUST match the 'action' attribute in your HTML form: /upload-image
// upload.single('image') handles a single file upload. 
// 'image' MUST match the 'name' attribute of your file input: <input type="file" name="image">
app.post('/upload-image', upload.single('image'), (req, res) => {
    // Check if a file was actually uploaded
    if (!req.file) {
        return res.status(400).send('No file was uploaded.');
    }

    // req.file contains all the file info
    console.log('File uploaded:', req.file);

    // Respond to the client
    res.send(`
        <h1>File Upload Success!</h1>
        <p>File saved to server as: <strong>${req.file.filename}</strong></p>
        <p>Original name: ${req.file.originalname}</p>
        <p><a href="/">Go back</a></p>
    `);
});

// --- 3. START THE SERVER ---
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});