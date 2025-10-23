# 1. Base Image
FROM node:20-alpine

# 2. Set Working Directory
WORKDIR /usr/src/app

# -------------------------------------------------------------
# 🌟 CONFIGURE PORT IN ONE PLACE: Set the Environment Variable
# This sets the variable read by server.js.
ENV PORT 8080

# 🌟 ADD EXPOSE FOR RELIABILITY
# This provides the necessary metadata/hint to the container runtime.
EXPOSE 8080
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
# The server.js reads the PORT environment variable defined above
CMD [ "npm", "start" ]