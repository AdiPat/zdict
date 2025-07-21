from setuptools import setup, Extension, find_packages
import os
import sys

# Read the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define the C extension module
ext_modules = [
    Extension(
        "zdict._zdictcore",
        sources=["zdict/_zdictcore.c", "zdict/swisstbl.c"],
        extra_compile_args=(
            ["-O3", "-Wall", "-Wextra"] if sys.platform != "win32" else ["/O2"]
        ),
    )
]

setup(
    name="zdict",
    version="1.0.0",
    author="Aditya Patange",
    author_email="aditya.patange@prodigaltech.com",
    description="Experimental high-performance dictionary implementation for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdiPat/zdict",
    packages=find_packages(),
    ext_modules=ext_modules,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: C",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    license="MIT",
    project_urls={
        "Bug Tracker": "https://github.com/AdiPat/zdict/issues",
        "Documentation": "https://github.com/AdiPat/zdict#readme",
        "Source Code": "https://github.com/AdiPat/zdict",
    },
)
