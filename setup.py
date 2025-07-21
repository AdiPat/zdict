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
        sources=[
            "zdict/_zdictcore.c",
            "zdict/_zdict_modes/mutable.c",
            "zdict/_zdict_modes/immutable.c",
            "zdict/_zdict_modes/readonly.c",
            "zdict/_zdict_modes/insert.c",
            "zdict/_zdict_modes/arena.c",
        ],
        include_dirs=["zdict/_zdict_modes"],
        # define_macros=[("Py_LIMITED_API", "0x03080000")],
        # py_limited_api=True,
        extra_compile_args=(
            ["-O3", "-Wall", "-Wextra"] if sys.platform != "win32" else ["/O2"]
        ),
    )
]

setup(
    name="zdict",
    version="1.0.0",
    author="AdiPat",
    author_email="aditya.patange@thehackersplaybook.org",
    description="Blazing-fast, drop-in replacement for Python's built-in dict with multiple high-performance modes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdiPat/zdict",
    packages=find_packages(),
    ext_modules=ext_modules,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
