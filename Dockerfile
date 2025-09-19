# Use the official Python image from the Docker Hub 
FROM python:3.10-slim

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the working directory in the container
WORKDIR /app

# Copy required files
COPY requirements.txt .
COPY static static
COPY templates templates
COPY scripts scripts
COPY website.py .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port that Flask runs on
EXPOSE 8080

# Command to run the Flask application when the container starts
CMD ["python", "website.py"]
