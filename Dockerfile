FROM python:3.11-slim

# Add retry logic and include OpenGL libraries
RUN apt-get update --option Acquire::Retries=5 \
    && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        xauth \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone LoLLMs-webui repository with submodules
RUN git clone --recursive https://github.com/ParisNeo/lollms-webui.git . && \
    git submodule update --init --recursive

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install  torch
RUN pip install -e lollms_core
RUN mkdir /app/personal_data
RUN echo "lollms_path: /app/lollms-webui/lollms_core/lollms\nlollms_personal_path: /app/personal_data" > /app/global_paths_cfg.yaml
# Expose default web UI port
EXPOSE 9600

# Set the entrypoint to our start script
CMD ["python", "/app/app.py", "--host", "0.0.0.0", "--force-accept-remote-access"]


