# 1. Base Image
FROM node:20-alpine

# 2. Set Working Directory
WORKDIR /usr/src/app

# 3. Create the uploads directory and ensure correct permissions
# -------------------------------------------------------------
RUN mkdir -p uploads && chmod 777 uploads
# -------------------------------------------------------------

# 4. Copy Dependency Files
COPY package*.json ./

# 5. Install Dependencies
RUN npm install

# 6. Copy Application Code
COPY . .

# 7. Expose Port
EXPOSE 8080

# 8. Start Command
CMD [ "npm", "start" ]