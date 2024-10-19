# A Dockerfile for a Python application that also make it possible to use sqlite3
# The source file is in src/main.py and the requirements.txt is for the packages
# that are needed to run the application

FROM python:3.10-slim

# Install sqlite3 and the packages that are needed to run the application
RUN apt-get update && apt-get install -y sqlite3 && \
    pip install --no-cache-dir -r requirements.txt

# Copy the source file and the requirements.txt to the container
COPY src/ /app/src/
COPY requirements.txt /app/

# Set the working directory to /app
WORKDIR /app

# Run the application
CMD ["python", "src/main.py"]
