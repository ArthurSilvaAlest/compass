FROM python:3.9-slim

WORKDIR /app

# Copiar arquivos necessários
COPY requirements.txt .
COPY api/ ./api/
COPY agent/ ./agent/

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor porta
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]