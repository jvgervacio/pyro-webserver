# Use the official Python 3.10 image as the base image
FROM python:3.10-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .
RUN sudo apt-get install build-essential libssl-dev libffi-dev python-dev
RUN python -m pip install --upgrade pip && \
    python -m pip install --upgrade setuptools && \
    python -m pip install --upgrade wheel
# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set the command to run when the container starts
CMD [ "python", "app.py" ]
