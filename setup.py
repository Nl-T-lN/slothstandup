from setuptools import setup, find_packages

setup(
    name="slothstandup",
    version="0.1.0",
    author="Nitin Pandey",
    author_email="nitinpandey11223@gmail.com",
    description="The zero-effort daily standup & timesheet ghostwriter powered by Gemma.",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/nitinpandey11223/slothstandup",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "slothstandup=slothstandup.cli:main",
            "sloth=slothstandup.cli:main",
        ],
    },
)
