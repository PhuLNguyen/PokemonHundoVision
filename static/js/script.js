// Get the form and result container elements
const form = document.getElementById('upload-form');
const resultContainer = document.getElementById('result-container');
const submitButton = document.getElementById('submit-button');

// Get elements for image preview
const imageInput = document.getElementById('image-input');
const uploadedImage = document.getElementById('uploaded-image');
const previewText = document.getElementById('preview-text');

// Event listener to display the selected file as an image preview
imageInput.addEventListener('change', function() {
	// Check if any file was selected
	if (this.files && this.files[0]) {
		const reader = new FileReader(); // API to read file content

		reader.onload = function(e) {
			// Set the image source to the data URL of the uploaded file
			uploadedImage.src = e.target.result;
			uploadedImage.style.display = 'block'; // Show the image element
			previewText.style.display = 'none';    // Hide the 'No image selected' text
		};

		// Read the image file as a Data URL (base64 encoded string)
		reader.readAsDataURL(this.files[0]);
	} else {
		// If no file is selected (e.g., user cancels selection)
		uploadedImage.src = '#';
		uploadedImage.style.display = 'none';
		previewText.style.display = 'block';
	}
});

// Add an event listener for the form submission
form.addEventListener('submit', async function(event) {
	// Prevent the default form submission (which would cause a page reload)
	event.preventDefault(); 

	// Clear previous results and show a loading message
	resultContainer.innerHTML = '<h2>Results</h2><p>Processing image... Please wait.</p>';
	submitButton.disabled = true; // Disable button to prevent double submission
	submitButton.textContent = 'Processing...';

	try {
		// Use the FormData API to easily capture the file input
		const formData = new FormData(form);
		
		// Perform the asynchronous POST request
		const response = await fetch(form.action, {
			method: form.method,
			body: formData,
		});

		const data = await response.json(); // Parse the JSON response

		// Check if the HTTP response was OK (status 200)
		if (response.ok) {
			// SUCCESS case
			const isHundo = data['HUNDO?'] === 'Yes';
			const hundoText = isHundo 
				? `<span class="success">${data['HUNDO?']}!</span>` 
				: `<span class="error">${data['HUNDO?']}</span>`;

			resultContainer.innerHTML = `
				<h2>OCR Success!</h2>
				<p><strong>Extracted Pokémon:</strong> ${data['Extracted Pokémon Name']}</p>
				<p><strong>Extracted CP:</strong> ${data['Extracted Combat Power (CP)']}</p>
				<p><strong>100% IV (HUNDO)?</strong> ${hundoText}</p>
				${isHundo ? `<p><strong>Pokemon Level:</strong> ${data['Pokemon Level']}</p>` : ''}
				<hr>
				<details>
					<summary>Vision API Raw Result</summary>
					<pre>${data['Vision API result']}</pre>
				</details>
			`;
		} else {
			// ERROR case (e.g., 400, 422, 500)
			resultContainer.innerHTML = `
				<h2 class="error">Error!</h2>
				<p>An error occurred during processing:</p>
				<p><strong>Status:</strong> ${response.status} - ${response.statusText}</p>
				<p><strong>Details:</strong> ${data.error || 'Unknown error. Check server logs.'}</p>
				<hr>
				<details>
					<summary>Vision API Raw Result</summary>
					<pre>${data['Vision API result']}</pre>
				</details>
			`;
		}
	} catch (e) {
		// Network or parsing error
		resultContainer.innerHTML = `
			<h2 class="error">Network Error!</h2>
			<p>Could not connect to the server or process the response.</p>
			<p>Details: ${e.message}</p>
		`;
	} finally {
		// Re-enable the button and reset its text after the operation completes
		submitButton.disabled = false;
		submitButton.textContent = 'Perform OCR';
		// Reset the file input so the user can immediately select a new file
		// Note: The file preview will automatically clear thanks to the 'change' listener logic
		form.reset(); 
	}
});