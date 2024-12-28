# Use a multi-stage build to reduce image size and improve security
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda \
    && rm Miniconda3-latest-Linux-x86_64.sh

# Add Conda to PATH
ENV PATH $PATH:/opt/conda/bin

# Create and activate Conda environment
RUN conda create --name lollms_env python=3.11 git pip -y

# Clone the repository
WORKDIR /app
RUN git clone --depth 1 --recurse-submodules https://github.com/ba2512005/lollms-webui.git \
    && cd lollms-webui \
    && conda run -n lollms_env bash -c "pip install -e ."

# Install project dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Build-time optimizations to reduce image size
RUN find /app -type f | xargs grep -oE '\n\s+$' | sed 's/^/rm /' | bash \
    && rm -rf /var/lib/apt/lists/* \
    && conda clean -a

# Final stage: production-ready environment
FROM python:3.11-slim

# Set working directory and copy application code
WORKDIR /app
COPY --from=builder /app/lollms-webui .

# Expose port 9600
EXPOSE 9600

# Set default command to run the application
CMD ["python", "app.py"]
