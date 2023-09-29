FROM ubuntu:22.04

# Remove any third-party apt sources to avoid issues with expiring keys.
RUN rm -f /etc/apt/sources.list.d/*.list

# Install some basic utilities.
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
 && rm -rf /var/lib/apt/lists/*

# Create a working directory.
RUN mkdir /app
WORKDIR /app

# Create a non-root user and switch to it.
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /app
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
USER user

# All users can use /home/user as their home directory.
ENV HOME=/home/user
RUN mkdir $HOME/.cache $HOME/.config \
 && chmod -R 777 $HOME

# Download and install Micromamba.
RUN curl -sL https://micro.mamba.pm/api/micromamba/linux-64/1.1.0 \
  | sudo tar -xvj -C /usr/local bin/micromamba
ENV MAMBA_EXE=/usr/local/bin/micromamba \
    MAMBA_ROOT_PREFIX=/home/user/micromamba \
    CONDA_PREFIX=/home/user/micromamba \
    PATH=/home/user/micromamba/bin:$PATH

# Set up the base Conda environment by installing PyTorch and friends.
COPY conda-linux-64.lock /app/conda-linux-64.lock
RUN micromamba create -qy -n base -f /app/conda-linux-64.lock \
 && rm /app/conda-linux-64.lock \
 && micromamba shell init --shell=bash --prefix="$MAMBA_ROOT_PREFIX" \
 && micromamba clean -qya

# Set the default command to python3.
CMD ["python3"]

################
# STAGE 2 OF 3 #
################ 
FROM base AS builder

COPY requirements.txt /tmp/

USER root

# Activate the Conda environment
RUN /home/user/micromamba/bin/conda init bash
SHELL ["/bin/bash", "-c"]
RUN source /home/user/micromamba/etc/profile.d/conda.sh && conda activate base

WORKDIR /srv

# Install local files as pip packagess
COPY ./app /srv/LoLLMsWebUI_server
COPY ./api /srv/api

RUN \
  apt-get update && \
  apt-get install -y python3-pip && \
  python3 /srv/LoLLMsWebUI_server/setup.py install && \
  python3 /srv/api/setup.py install && \
  pip install --no-cache-dir \
    -r /tmp/requirements.txt && \
  rm /tmp/requirements.txt && \
  rm -rf /srv/LoLLMsWebUI_server \
         /srv/api


################
# STAGE 3 OF 3 #
################ 
FROM builder as APP

WORKDIR /srv

COPY ./app.py /srv/app.py
COPY ./static /srv/static
COPY ./templates /srv/templates
COPY ./web /srv/web
COPY ./assets /srv/assets
COPY ./configs /src/configs
COPY ./restart_script.py /srv/restart_script.py
COPY global_paths_cfg.yaml /srv/global_paths_cfg.yaml


ENV SHELL=/bin/bash

EXPOSE 9600


CMD ["python", "app.py", \
    "--host", "0.0.0.0", \
    "--port", "9600", \
    "--db_path", "/data/Documents/databases/database.db", \
    "--config", "/configs/config.yaml"]

# python app.py --host 0.0.0.0 --port 9600 --db_path /data/Documents/databases/database.db --config /configs/config.yaml