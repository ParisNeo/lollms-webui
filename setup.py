from pathlib import Path
from typing import Union

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


def read_requirements(path: Union[str, Path]):
    with open(path, "r") as file:
        return file.read().splitlines()


requirements = read_requirements("requirements.txt")
requirements_dev = read_requirements("requirements_dev.txt")

setuptools.setup(
    name="GPT4Allui",
    version="0.0.5",
    author="Saifeddine ALOUI",
    author_email="aloui.saifeddine@gmail.com",
    description="A web ui for running chat models with different backends. Supports multiple personalities and extensions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nomic-ai/gpt4all-ui",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    extras_require={"dev": requirements_dev},
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
)
