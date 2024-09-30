# Stage 1: Build the React app
FROM node:14 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .


WORKDIR /app/app

# Build the React app for production
RUN npm run build

# Stage 2: Setup NGINX for serving the app and reverse proxy
FROM nginx:alpine

# Remove the default NGINX config
RUN rm /etc/nginx/conf.d/default.conf

# Copy the custom NGINX config file
COPY nginx.conf /etc/nginx/conf.d

# Copy the build output from the React app (from the first stage)
COPY --from=build /app/app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]