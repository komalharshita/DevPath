import os

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
    
    # Metadata settings
    SITE_NAME = os.environ.get("SITE_NAME", "DevPath")
    SITE_DESCRIPTION = os.environ.get("SITE_DESCRIPTION", "Recommend real coding projects based on your skills.")
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
    OG_IMAGE_PATH = os.environ.get("OG_IMAGE_PATH", "static/images/og-image.png")

    @classmethod
    def get_base_url(cls):
        return cls.BASE_URL.rstrip('/')

    @classmethod
    def get_og_image_url(cls):
        return f"{cls.get_base_url()}/{cls.OG_IMAGE_PATH.lstrip('/')}"
