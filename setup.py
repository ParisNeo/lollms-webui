from pathlib import Path
from typing import Union

import setuptools

README_MD_FILE = "README.md"
REQUIREMENTS_TXT_FILE = "requirements.txt"
REQUIREMENTS_DEV_TXT_FILE = "requirements_dev.txt"

with open(README_MD_FILE, "r") as fh:
    long_description = fh.read()

def read_requirements(path: Union[str, Path]) -> list:
    with open(path, "r") as file:
        return [line.strip() for line in file.readlines()]

requirements = list(filter(None, read_requirements(REQUIREMENTS_TXT_FILE)))
requirements_dev = list(filter(None, read_requirements(REQUIREMENTS_DEV_TXT_FILE)))

requirements = read_requirements("requirements.txt")
requirements_dev = read_requirements("requirements_dev.txt")

setuptools.setup(
    name="Lollms-webui",
    version="5.0.3",
    author="Saifeddine ALOUI",
    author_email="aloui.saifeddine@gmail.com",
    description="A web ui for running chat models with different bindings. Supports multiple personalities and extensions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ba2512005/lollms-webui",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
)
