# Use the official Python base image for Raspberry Pi
FROM arm32v7/python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev cargo curl gcc

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the requirements file to the working directory
COPY requirements.txt .

# update pip 
RUN pip install --upgrade pip

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set the command to run when the container starts
CMD [ "python", "app.py" ]
