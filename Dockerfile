FROM python:3.11-slim

# Imposta la directory di lavoro dentro il container
WORKDIR /app

# Copia solo il file requirements prima (per ottimizzare cache)
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice dell'app
COPY . .

# Esponi la porta (Cloud Run la imposterà automaticamente)
EXPOSE 8000

# Comando per avviare l'app
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}