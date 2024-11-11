# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim

ENV PYTHONUNBUFFERED True
# Copy the requirements file
COPY requirements.txt .

# Install project dependencies. It's best practice to pin library versions
# in your requirements.txt for reproducible builds.
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory in the container
WORKDIR /app

# Copy project filesCOPY . /app
COPY . /app

# Create a non-root user for security best practices (optional but recommended).
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8080
# Command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]

