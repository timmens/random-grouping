from setuptools import find_packages
from setuptools import setup

setup(
    name="randomgroups",
    version="0.0.1",
    author="Tim Mensinger",
    author_email="tmensinger@uni-bonn.de",
    url="https://github.com/timmens/random-grouping",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=["click", "numpy >=1.16", "pandas >=0.24"],
)
