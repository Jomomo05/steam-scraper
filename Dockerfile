# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (sqlite3 is required)
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker caching)
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . /app

# Ensure proper permissions
RUN chmod +x /app/main.py

# Run the Python script when the container launches
CMD ["python3", "/app/main.py"]
