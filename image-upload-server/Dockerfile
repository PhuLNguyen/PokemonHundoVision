# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# Set the port the application listens on (as defined in server.py)
ENV PORT 8080
# Set the working directory in the container
WORKDIR /app

# Install any dependencies specified in your requirements file.
# We explicitly install the required libraries here.
# It's best practice to use a requirements.txt, but for simplicity, we install directly.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The Google Cloud Vision API needs the client library
# We already covered this in the requirements.txt, but if you were to install 
# it directly: RUN pip install google-cloud-vision

# Copy the server.py into the container
COPY server.py .

# Optional: If you are running this locally or in a non-GCP environment,
# you would uncomment the following lines and place your service account
# key file (e.g., 'keyfile.json') in your app directory.
# ENV GOOGLE_APPLICATION_CREDENTIALS=/app/keyfile.json
# COPY keyfile.json .

# Expose the port the app runs on
EXPOSE ${PORT}

# Run the server.py script using Gunicorn for production, or the built-in Flask server.
# For simplicity and Cloud Run compatibility, we use the built-in server here:
# CMD ["python", "server.py"]

# A more robust solution for production, using Gunicorn
# First, install gunicorn: RUN pip install gunicorn
# Then, use gunicorn to run the Flask app defined in server.py
# The format is 'module:app_object_name' (e.g., server:app)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]