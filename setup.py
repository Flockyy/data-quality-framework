from setuptools import find_packages, setup


with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="data-quality-framework",
    version="0.1.0",
    author="Flockyy",
    author_email="your.email@example.com",
    description="A comprehensive data quality validation, profiling, and monitoring framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Flockyy/data-quality-framework",
    packages=find_packages(exclude=["tests*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dqf=dqf.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dqf": ["templates/*.html", "templates/*.md"],
    },
)
