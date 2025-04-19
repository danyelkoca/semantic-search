# # Use an official Node.js runtime as the base image
# FROM node:20-alpine

# # Set the working directory
# WORKDIR /app

# # Copy package.json and package-lock.json (or package.json and pnpm-lock.yaml)
# COPY package*.json ./

# # Install dependencies
# RUN npm install

# # Copy all other frontend files
# COPY . .

# # Build the SvelteKit app
# RUN npm run build

# # Expose the port used by SvelteKit preview server
# EXPOSE 4173

# # Start the app in preview mode on all network interfaces
# CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]


# Stage 1: Build
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:stable-alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]