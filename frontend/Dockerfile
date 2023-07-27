# pull ubuntu based node image
FROM node:18

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install app dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm ci

# add app
COPY . ./

# build
RUN npm run build

# serve
RUN npm install -g serve
CMD ["serve", "-s", "build"]
 
