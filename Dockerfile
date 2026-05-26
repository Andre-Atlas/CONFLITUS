# Dockerfile (Raiz)
FROM node:22-alpine

# Definir diretório de trabalho
WORKDIR /app

# Copiar ficheiros de dependências
COPY package.json package-lock.json* ./

# Instalar dependências
RUN npm install

# Copiar todo o código fonte (frontend e proxy)
COPY . .

# Fazer a compilação (build) para produção
RUN npm run build

# Expor a porta do servidor Express
EXPOSE 3000

# Iniciar o servidor compilado
CMD ["npm", "start"]