# config.py
# Application configuration settings for DevPath.
#
# This module centralizes all configuration values that might change
# between environments (development, production, forks).

import os

class Config:
    """Base configuration class with sensible defaults."""
    
    # Base URL for the application - used for OG tags and canonical URLs
    # Can be overridden via environment variable for different deployments
    BASE_URL = os.getenv("BASE_URL", "https://mydevpath-github.vercel.app")
    # Security and Session
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    
    # GitHub OAuth Settings
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "dummy_client_id")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "dummy_client_secret")
    
    # Database Settings
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(basedir, "data", "devpath.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application metadata for OG tags
    SITE_NAME = "DevPath"
    SITE_DESCRIPTION = "Get personalized coding project recommendations with step-by-step roadmaps and starter code."
    
    # OG image path (relative to static folder)
    OG_IMAGE_PATH = "/static/og-banner.png"
    
    @classmethod
    def get_og_image_url(cls):
        """Return the full URL for the OG banner image."""
        return f"{cls.BASE_URL.rstrip('/')}{cls.OG_IMAGE_PATH}"
    
    @classmethod
    def get_base_url(cls):
        """Return the base URL without trailing slash."""
        return cls.BASE_URL.rstrip("/")
