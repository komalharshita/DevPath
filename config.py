# config.py
import os

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
