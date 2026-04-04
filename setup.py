#!/usr/bin/env python3
"""
Setup script for OpenEnv CRM Query Environment
"""

from setuptools import setup, find_packages

setup(
    name="openenv-crm-query",
    version="1.0.0",
    description="OpenEnv-compliant CRM Query Environment for multi-step reasoning tasks",
    author="OpenEnv Hackathon",
    author_email="hackathon@openenv.ai",
    url="https://github.com/Nihar1402-iit/OpenEnv-Hackathon",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "openai>=1.3.0",
        "openenv>=0.1.13",
        "pyyaml>=6.0.1",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.24.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    include_package_data=True,
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "openenv-crm-server=server.app:main",
        ],
    },
)
