# Use a Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies needed for pygithub and git operations
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy action code
COPY entrypoint.py /entrypoint.py
COPY templates/ /templates/

# Make sure entrypoint is executable
RUN chmod +x /entrypoint.py

# Run the entrypoint script
ENTRYPOINT ["python", "/entrypoint.py"]
