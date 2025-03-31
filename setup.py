from setuptools import setup, find_packages

setup(
    name="newscast",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.12.3",
        "requests>=2.31.0",
        "openai>=1.12.0",
        "python-dotenv>=1.0.1",
        "elevenlabs>=1.13.5",
        "pydantic>=2.6.3",
        "fastapi>=0.110.0",
        "uvicorn>=0.27.1",
        "python-multipart>=0.0.9",
        "pydub>=0.25.1"
    ],
) 