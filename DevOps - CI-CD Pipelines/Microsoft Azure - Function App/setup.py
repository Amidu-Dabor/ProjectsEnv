from setuptools import setup, find_packages

setup(
    name="azure_storage_project",  # Your package name
    version="0.1.0",
    author="Amidu Dabor",
    author_email="daboramidu93@gmail.com",
    description="A package for Azure storage management using Python SDK.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Amidu-Dabor/azure_storage_project",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "azure-identity",
        "azure-mgmt-resource",
        "azure-mgmt-storage",
    ],
)
