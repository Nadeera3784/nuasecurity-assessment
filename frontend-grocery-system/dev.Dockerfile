FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json*  ./

RUN npm install 

COPY . .

COPY public ./public

COPY vite.config.ts .

COPY tsconfig.json .

COPY src ./src

CMD npm run dev -- --host 0.0.0.0