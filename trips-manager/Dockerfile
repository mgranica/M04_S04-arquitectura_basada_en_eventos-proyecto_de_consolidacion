# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install project requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

# Copy the current directory contents into the container at /app
COPY app.py /opt/

# Set the working directory to /app
WORKDIR /opt/

EXPOSE 8001

# Run the application using Waitress on port 5005
CMD ["python3", "app.py"]