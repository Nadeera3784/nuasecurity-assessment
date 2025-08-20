FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json*  ./

RUN npm install 

COPY . .

COPY public ./public

COPY next.config.ts .

COPY tsconfig.json .

ENV NEXT_TELEMETRY_DISABLED 1

CMD npm run dev