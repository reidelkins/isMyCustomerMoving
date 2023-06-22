# Stage 1: Install dependencies
FROM node:18.9.0-alpine as dependencies-stage
WORKDIR /frontend
COPY package*.json ./
RUN yarn install --silent

# Stage 2: Build React application
FROM dependencies-stage as build-stage
WORKDIR /frontend
COPY . .
RUN yarn build

# Stage 3: Serve React application with Nginx
FROM nginx:1.21-alpine
COPY --from=build-stage /frontend/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
