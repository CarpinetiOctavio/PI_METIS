# F9 (docs/frontend/informe-diagnostico-ui-rota.md): docker-compose.yml
# declaraba `frontend: build: ./frontend` desde el principio, pero este
# archivo nunca existió — `docker-compose up --build` fallaba directo.
# Multi-stage: node para build, nginx para servir el estático — el
# frontend nunca corre `npm run dev` en producción.
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
