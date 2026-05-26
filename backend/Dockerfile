# backend/Dockerfile
FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar os requisitos e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante código do backend
COPY . .

# Expor a porta que o FastAPI utiliza
EXPOSE 8000

# Comando para iniciar o servidor Uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]