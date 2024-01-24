# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the current directory to the container
COPY . .

# ARG to be passed during build for DEV environment
ARG DEV

# Set environment variable DEV based on build argument
ENV DEV=${DEV}

# Expose the default ports for Streamlit
# EXPOSE 8501
# EXPOSE 8502

# Set the entrypoint for the container
CMD streamlit run main.py --server.port=$(if [ "$DEV" = "True" ]; then echo 8502; else echo 8501; fi)