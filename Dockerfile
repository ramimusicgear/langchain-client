# Use the official Streamlit image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python requirements file
RUN pip install --no-cache-dir streamlit extra-streamlit-components requests pymongo python-dotenv pyjwt

# Copy all files from the current directory to the container
COPY . .

# Expose the port the Streamlit app runs on
EXPOSE 8501

# Set the entrypoint for the container
CMD ["streamlit", "run", "client.py"]
