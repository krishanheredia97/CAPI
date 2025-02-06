from setuptools import setup, find_packages
setup(
    name="capi",  
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "pyperclip",
    ],
    entry_points={
        "console_scripts": [
            "capi=capi.cli:main", 
        ],
    },
)