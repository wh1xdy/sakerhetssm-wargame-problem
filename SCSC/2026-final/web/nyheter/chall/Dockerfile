FROM node:18-alpine

WORKDIR /app

ENV DB_HOST=nyheter-db
ENV DB_USER=news_user
ENV DB_PASSWORD=news_password
ENV DB_NAME=news_db

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000


CMD ["node", "server.js"]
