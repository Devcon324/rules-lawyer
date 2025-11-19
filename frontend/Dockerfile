# Use Node.js LTS version
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Default command (can be overridden in docker-compose)
CMD ["npm", "run", "dev", "--", "--host"]

