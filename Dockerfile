# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONNOUSERSITE=1 \
    PYTHONPATH="" \
    PYTHONHOME="" \
    TEMP="/installer_files/temp" \
    TMP="/installer_files/temp" \
    MINICONDA_DIR="/installer_files/miniconda3" \
    INSTALL_ENV_DIR="/installer_files/lollms_env" \
    PACKAGES_TO_INSTALL="python=3.11 git pip"

# Create necessary directories
RUN mkdir -p /installer_files/temp /installer_files/miniconda3 /installer_files/lollms_env

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniconda
RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p $MINICONDA_DIR && \
    rm Miniconda3-latest-Linux-x86_64.sh

# Initialize conda
RUN $MINICONDA_DIR/bin/conda init bash

# Create and activate the conda environment
RUN $MINICONDA_DIR/bin/conda create -y -p $INSTALL_ENV_DIR $PACKAGES_TO_INSTALL && \
    $MINICONDA_DIR/bin/conda install -y conda

# Clone the repository and install dependencies
RUN git clone --depth 1 --recurse-submodules https://github.com/ParisNeo/lollms-webui.git && \
    cd lollms-webui && \
    git submodule update --init --recursive && \
    cd lollms_core && \
    pip install -e . && \
    cd ../utilities/pipmaster && \
    pip install -e . && \
    cd ../.. && \
    pip install -r requirements.txt

# Set the working directory
WORKDIR /lollms-webui

# Default command
CMD ["bash"]