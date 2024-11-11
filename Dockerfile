# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install project dependencies. It's best practice to pin library versions
# in your requirements.txt for reproducible builds.
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create a non-root user for security best practices (optional but recommended).
RUN useradd -ms /bin/bash appuser
USER appuser

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Set environment variables (Important! Replace with your actual values or use secrets).

# For WhatsApp:
ENV WHATSAPP_TOKEN="your_whatsapp_token"
ENV WHATSAPP_PHONE_NUMBER_ID="your_whatsapp_phone_number_id"

# For RapidPro:
ENV RAPIDPRO_URL="your_rapidpro_url"
ENV RAPIDPRO_TOKEN="your_rapidpro_token"

# For Database:
ENV DATABASE_URL="your_database_url"  

# For Gemini :
ENV GEMINI_API_KEY="your_gemini_api_key"

# For Webhook verification:
ENV VERIFY_TOKEN="your_verify_token"

# For Facebook app ID:
ENV APP_SECRET="your_app_secret"

# Command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
