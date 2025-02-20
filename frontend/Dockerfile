# Etapa de construcción (Build)
FROM node:18-alpine as build
WORKDIR /app

# Copiar package.json e instalar dependencias
COPY package*.json ./
RUN npm install

# Copiar el resto del código fuente
COPY . .

# 🔹 Generar la build de Vite (esto creará /app/dist)
RUN npm run build

# 🔹 Verificar si la build se generó correctamente
RUN ls -lah /app/dist || echo "ERROR: No se generó dist/"

# Etapa de producción con Nginx
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# 🔹 Copiar la build generada en la etapa anterior
COPY --from=build /app/dist/ .

# Copiar la configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
