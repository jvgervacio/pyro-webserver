# Use the official Python 3.10 image as the base image
FROM python:3.10-alpine3.19

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

RUN python -m pip install --upgrade pip
# Install the Python dependencies

RUN  ln -sf /usr/share/zoneinfo/Asia/Manila /etc/timezone && \
     ln -sf /usr/share/zoneinfo/Asia/Manila /etc/localtime && \
     pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set the command to run when the container starts
CMD [ "python", "app.py" ]
