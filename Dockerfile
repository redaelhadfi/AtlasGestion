# Use Ubuntu base image
FROM ubuntu:plucky-20241213

# Set environment variables to prevent Python from writing .pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Update and install required system libraries
RUN apt-get update -y && apt-get install -y \
    python3 python3-pip python3-venv \
    mysql-client libmysqlclient-dev pkg-config build-essential \
    libcairo2 libcairo2-dev libpango-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Create a virtual environment and install Python dependencies
RUN python3 -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Update PATH to use the virtual environment by default
ENV PATH="/opt/venv/bin:$PATH"

# Copy the rest of the application code into the container
COPY . .

# Expose the Django development server port
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
