FROM python:3.11

# Install libzbar0
RUN apt-get update && apt-get install -y libzbar0

# Set working directory
WORKDIR /app

COPY . /app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
EXPOSE 8000

# Set the entrypoint command
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]