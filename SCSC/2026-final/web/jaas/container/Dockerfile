FROM node:25-alpine

WORKDIR /app
RUN apk add curl

COPY package.json package-lock.json /app/
RUN npm ci

COPY server.js index.html .FLAG.txt /app/

EXPOSE 3000
CMD ["npm", "start"]
HEALTHCHECK --start-period=20s --start-interval=1s CMD curl -f http://127.0.0.1:3000/ || exit 1
