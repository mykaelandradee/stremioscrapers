FROM python:3.12-slim

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos da aplicação
COPY . .

# Porta do Flask
EXPOSE 7000

# Inicia a aplicação
CMD ["python", "app.py"]