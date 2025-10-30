# Dockerfile for Cloud Run deployment of notion-language

# Light Python image
FROM python:3.11-slim

# Forbid creating pyc files and force instant logs display
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Define the working directory inside the container
WORKDIR /app

# Copy and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project files into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8080

# Launch the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
