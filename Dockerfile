# A simplified, modern Dockerfile for the GOB System

# 1. Use a standard, slim Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install essential system dependencies
# git is needed by some python libraries, ssh for remote code execution feature
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ssh \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy and install Python dependencies first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Install Playwright browsers (required by the application)
RUN playwright install --with-deps

# 7. Expose the port the application will run on
EXPOSE 80

# 8. Define the command to run the application
# This starts the FastAPI server for the UI and agent.
CMD ["python", "general-operations-bots/run_ui.py", "--dockerized=true", "--port=80", "--host=0.0.0.0"]
