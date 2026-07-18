# ═══════════════════════════════════════════════════════════════
# QwenGuard AI - Alibaba Cloud Deployment
# Dockerfile for ECS / Container Service
# ═══════════════════════════════════════════════════════════════
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Solidity compiler
RUN pip install py-solc-x && python -c "from solcx import install_solc; install_solc('0.8.20')"

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "app.py", "server"]
