FROM python:3.10

# Install sqlite3 and cron
RUN apt-get update && apt-get install -y sqlite3 cron

# Set the working directory
WORKDIR /app

# Copy files to the container
COPY crontab /etc/cron.d/mycron
COPY src/ /app/src/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Adjust permissions and install cron job
RUN chmod 0644 /etc/cron.d/mycron
RUN crontab /etc/cron.d/mycron

# Run cron in the foreground
CMD ["cron", "-f"]
