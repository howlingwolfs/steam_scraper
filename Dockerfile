# Use a lightweight Python image matching your project version
FROM python:3.13.5-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This step is often done first to leverage Docker's caching mechanism
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code into the container
COPY app/ ./app/

# Define the command to run your application
CMD ["python", "app/app.py"]