# config.py
# Application configuration settings for DevPath.
#
# This module centralizes all configuration values that might change
# between environments (development, production, forks).

import os

class Config:
    """Base configuration class with sensible defaults."""
    
    # Secret key for session signing and CSRF protection
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-in-production")
    
    # Base URL for the application - used for OG tags and canonical URLs
    # Can be overridden via environment variable for different deployments
    BASE_URL = os.getenv("BASE_URL", "https://mydevpath-github.vercel.app")
    
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
