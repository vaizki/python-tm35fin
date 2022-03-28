"""
    Package setup script for ETRS-TM35FIN coordinate system helper classes
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tm35fin",
    version="0.1.1",
    author="Jukka Vaisanen",
    author_email="vaizki@vaizki.fi",
    description="ETRS-TM35FIN coordinate system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vaizki/python-tm35fin",
    project_urls={
        "Bug Tracker": "https://github.com/vaizki/python-tm35fin/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.8",
)
