FROM python:3.11-slim

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    curl \
    libcurl4 \
    wget && \
    rm -rf /var/lib/apt/lists/*

# Copy the Chrome installer from the root of the project to the image
COPY google-chrome-stable_current_amd64.deb /tmp/

# Install Google Chrome from the local path
RUN apt-get install -y /tmp/google-chrome-stable_current_amd64.deb && \
    rm /tmp/google-chrome-stable_current_amd64.deb

# Display Chrome version
RUN echo "Chrome: " && google-chrome --version

# Set working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Set the default command
CMD ["python", "run.py"]
