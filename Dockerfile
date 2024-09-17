# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy required files
COPY requirements.txt .
COPY static static
COPY templates templates
COPY website.py .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Flask runs on
EXPOSE 8080

# Define the command to run your Flask application when the container starts
CMD ["python", "website.py"]
