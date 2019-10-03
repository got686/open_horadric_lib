from setuptools import find_namespace_packages
from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="open_horadric_lib",
    version="0.0.2dev",
    packages=find_namespace_packages(),
    install_requires=requirements,
    url="https://github.com/got686/open_horadric_lib",
    license="MIT",
    author="got686",
    author_email="got686@yandex.ru",
    description="Library for open_horadric project and generated code",
)
