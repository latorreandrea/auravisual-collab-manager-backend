FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first (to optimize cache)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the app code
COPY . .

# Expose the port (Cloud Run will set it automatically)
EXPOSE 8080

# Command to start the app
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT