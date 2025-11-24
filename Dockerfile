# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install essential system dependencies required by OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install any dependencies specified in your requirements file.
# We explicitly install the required libraries here.
# It's best practice to use a requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server.py and templates directory into the container
COPY server.py postprocessing.py preprocessing.py ./
COPY templates /app/templates

# Copy pokemon data to container
COPY pokemon-data/hundo-data.jsonl /app/

# Set environment variables
# Set the port the application listens on (as defined in server.py)
ENV PORT=8080

# Python interpreter automatically forces all standard streams (stdout, stderr) to be unbuffered.
#   Which show all output immediately in Cloud Run log
ENV PYTHONUNBUFFERED 1

# Expose the port the app runs on
EXPOSE ${PORT}

# This is the "exec" form, but it invokes /bin/sh -c to handle the variable substitution.
CMD ["/bin/sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} server:app"]