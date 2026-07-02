from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="digital-clock-multi-timezone",
    version="1.0.0",
    author="AhmedElsakaVip",
    author_email="contact@example.com",
    description="A beautiful digital clock displaying time across multiple time zones",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AhmedElsakaVip/digital-clock",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pytz>=2023.3",
        "python-dateutil>=2.8.2",
    ],
)
