# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda \
    && rm Miniconda3-latest-Linux-x86_64.sh

# Add Conda to PATH
ENV PATH /opt/conda/bin:$PATH

# Create and activate Conda environment
RUN conda create --name lollms_env python=3.11 git pip -y
SHELL ["conda", "run", "-n", "lollms_env", "/bin/bash", "-c"]

# Clone the repository
RUN git clone --depth 1 --recurse-submodules https://github.com/ParisNeo/lollms-webui.git \
    && cd lollms-webui/lollms_core \
    && pip install -e . \
    && cd ../.. \
    && cd lollms-webui/utilities/pipmaster \
    && pip install -e . \
    && cd ../..

# Install project dependencies
WORKDIR /app/lollms-webui
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 9600
EXPOSE 9600

# Set the default command to run the application
CMD ["python", "app.py"]