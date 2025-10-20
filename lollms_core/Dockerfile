# Use an official Python runtime as a parent image
#FROM ai_ticket
ARG BASE_IMAGE
FROM ${BASE_IMAGE} 

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN apt update
RUN apt install -y git
RUN pip install --trusted-host pypi.python.org -r requirements.txt


COPY ./elf_docker_cfg /app/elf_docker_cfg
COPY ./lollms /app/lollms
COPY ./README.md /app/README.md
COPY ./MANIFEST.in /app/MANIFEST.in
COPY ./LICENSE /app/LICENSE
COPY ./requirements_dev.txt /app/requirements_dev.txt
COPY ./requirements.txt /app/requirements.txt
COPY ./setup.py /app/setup.py
COPY ./zoos /app/zoos
COPY ./configs /app/configs
RUN pip install -e .

# Run app.py when the container launches
CMD ["lollms-elf","--host","0.0.0.0", "--port", "9601", "--default_cfg_path", "/app/elf_docker_cfg/config_paths.yaml"]

