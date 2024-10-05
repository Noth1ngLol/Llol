from setuptools import setup, find_packages
import setuptools.command.build_py  # Ensure setuptools is correctly imported
import subprocess
import os

# Custom command to build Rust components if needed
class CustomBuildCommand(setuptools.command.build_py.build_py):
    """Custom build command to compile Rust components."""
    def run(self):
        # Check if Cargo (Rust toolchain) is installed
        if subprocess.call(["cargo", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0:
            print("Building Rust components...")
            subprocess.run(["cargo", "build", "--release"], check=True)
        else:
            print("Warning: Rust is not installed. Skipping Rust build.")
        setuptools.command.build_py.build_py.run(self)

# Function to read requirements from requirements.txt
def parse_requirements():
    requirements = []
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            requirements = f.read().splitlines()
    return requirements

setup(
    name="gguf_modifier",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements(),  # Load dependencies
    entry_points={
        "console_scripts": [
            "GE=frontend.main:main",  # Map the "GE" command to the main script
        ],
    },
    cmdclass={
        'build_py': CustomBuildCommand,  # Add custom build command
    },
    description="A tool for modifying and managing GGUF metadata files.",
    author="Your Name",
    url="https://github.com/Noth1ngLol/Llol.git",
    author_email="your.email@example.com",
    classifiers={
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    },
    python_requires=">=3.6",
)
