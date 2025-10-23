# 1. Base Image
# Use a Node.js Long Term Support (LTS) image as the foundation.
# This ensures all modern features (like 'node:events') are supported.
FROM node:20-alpine

# 2. Set Working Directory
# Define the directory where the app code will live inside the container
WORKDIR /usr/src/app

# 3. Copy Dependency Files
# Copy package.json and package-lock.json to the workdir
# This step is cached, speeding up rebuilds if only application code changes
COPY package*.json ./

# 4. Install Dependencies
# Install Node.js dependencies
RUN npm install

# 5. Copy Application Code
# Copy the rest of the application source code into the container
COPY . .

# 6. Expose Port
# Inform Docker that the container listens on port 3000 at runtime
EXPOSE 8080

# 7. Start Command
# Define the command to run the application when the container starts
CMD [ "npm", "start" ]