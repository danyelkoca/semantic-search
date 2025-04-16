FROM nginx:alpine

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static files
COPY static/ /usr/share/nginx/html/
