from setuptools import setup, find_packages

setup(
    name="vef-state-engine",
    version="1.0.0",
    description="Volume-to-Force Differential State Engine - Physics simulation framework for coupled oscillatory systems",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mark Chrisman",
    author_email="markchrismanppnf@gmail.com",
    url="https://github.com/markchrismanppnf-hash/VEF-state-engine",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "matplotlib>=3.3.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=[
        "physics",
        "simulation",
        "oscillatory-systems",
        "phase-coupling",
        "energy-dynamics",
        "numerical-integration",
    ],
    project_urls={
        "Documentation": "https://github.com/markchrismanppnf-hash/VEF-state-engine#readme",
        "Source Code": "https://github.com/markchrismanppnf-hash/VEF-state-engine",
        "Bug Tracker": "https://github.com/markchrismanppnf-hash/VEF-state-engine/issues",
    },
)
