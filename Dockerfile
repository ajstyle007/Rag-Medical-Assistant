FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=300 -r requirements.txt

# Copy all source files
COPY . .

# Copy and make start.sh executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose the port required by Hugging Face Spaces
EXPOSE 7860

# Set the default command to run the start script using bash
CMD ["bash", "/start.sh"]
