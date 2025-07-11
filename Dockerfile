# Dockerfile
# Use a Debian version with an older GLIBC for compatibility
FROM debian:bullseye-slim

# Set working directory inside the container
WORKDIR /app

# Install necessary build tools and Python
# build-essential for compiling, python3-pip for pip
# patchelf might be useful for some PyInstaller scenarios, though not always needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.13 \
    python3-pip \
    python3-dev \
    python-dev \
    build-essential \
    upx-ucl \
    && \
    rm -rf /var/lib/apt/lists/*

# Copy your Python application files into the container
COPY . /app

# Install PyInstaller and your application's Python dependencies
RUN pip3 install -r /app/requirements.txt

# Build the PyInstaller executable
# --onefile creates a single executable
# --clean removes build caches
# --strip and --noupx are often used for smaller binaries, but check compatibility
RUN pyinstaller --onefile --name=dbmanager --clean --noconfirm --hidden-import=datebase db_manager.py

# The executable will be in /app/dist/your_script
# You might want to copy it out in a final stage, or use the GitHub Action to retrieve it.