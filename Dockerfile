# Use a base image of Python
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the necessary dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the source code to the container image
COPY timeExporter.py .

# Expose the port where the Prometheus server will run
EXPOSE 8000

# Define the default command to run the script
CMD ["python", "-u", "timeExporter.py"]
