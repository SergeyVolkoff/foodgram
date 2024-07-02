# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install npm@10.8.1
COPY . ./
RUN npm run build
CMD cp -r build result_build
