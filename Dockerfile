# Use the official Python image as the base image
FROM python:3.10-slim

# Install dependencies for Selenium and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libxcursor1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    xdg-utils \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/Linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

RUN which google-chrome

# Update the package list and install wget, unzip, and Firefox
# RUN apt-get update && apt-get install -y wget unzip \
#     && apt-get install -y firefox-esr \
#     && apt-get clean
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app
# WORKDIR /app

COPY --chown=user . $HOME/app
# COPY . /app
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Selenium script
# CMD ["gunicorn", "-b", "0.0.0.0:7860","app:app"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
