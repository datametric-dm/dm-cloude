FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci || npm install
COPY . .
RUN npm i -g serve
EXPOSE 3000
CMD sh -lc 'if npm run | grep -qE "^  build"; then npm run build && serve -s build -l 3000; else npm start; fi'
