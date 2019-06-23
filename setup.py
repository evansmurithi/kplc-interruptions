import os
from setuptools import find_packages, setup

from kplc_interruptions import VERSION

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
README_FILE = os.path.join(BASE_DIR, "README.md")

with open(README_FILE) as f:
    README = f.read()

setup(
    name="kplc_interruptions",
    version=VERSION,
    description="KPLC's planned power interruptions scraper",
    long_description=README,
    author="Evans Murithi",
    author_email="murithievans80@gmail.com",
    url="https://github.com/evansmurithi/kplc-interruptions",
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=[
        "environs[django]==4.2.0",
        "psycopg2-binary==2.8.3",
        "requests==2.22.0",
        "beautifulsoup4==4.7.1",
        "pdftotext==2.1.1",
        "django==2.2",
    ],
    scripts=[],
    include_package_data=True,
)
