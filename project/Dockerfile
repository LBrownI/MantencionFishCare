# Use Python 3.12-slim as base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the Flask application port
EXPOSE 5000

# Run the Flask application
# CMD ["flask", "run", "--host=0.0.0.0"]
