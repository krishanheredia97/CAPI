from setuptools import setup, find_packages
setup(
    name="capi",  
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "pyperclip",
        "prompt_toolkit",
        "loguru",
        "openai",
        "python-dotenv",
        "termcolor",
    ],
    entry_points={
        "console_scripts": [
            "capi=capi.cli:main", 
        ],
    },
)