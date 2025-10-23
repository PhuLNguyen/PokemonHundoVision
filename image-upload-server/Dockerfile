# 1. Base Image
FROM node:20-alpine

# 2. Set Working Directory
WORKDIR /usr/src/app

# -------------------------------------------------------------
# 🌟 CONFIGURE PORT IN ONE PLACE: Set the Environment Variable
# Cloud Run expects the app to listen on the port defined by the 
# PORT environment variable, which it defaults to 8080.
ENV PORT 8080
# -------------------------------------------------------------

# 3. Create the uploads directory and ensure correct permissions
RUN mkdir -p uploads && chmod 777 uploads

# 4. Copy Dependency Files
COPY package*.json ./

# 5. Install Dependencies
RUN npm install

# 6. Copy Application Code
COPY . .

# 7. Start Command
# The server.js will read the PORT environment variable defined above
CMD [ "npm", "start" ]