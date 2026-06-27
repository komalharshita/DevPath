# config.py
# Application configuration settings for DevPath.
#
# This module centralizes all configuration values that might change
# between environments (development, production, forks).

import os
import json
from pathlib import Path

class Config:
    """Base configuration class with sensible defaults."""
    
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
    @classmethod
    def load_recommendation_weights(cls):
        """
        Load recommendation scoring weights from config file.
        
        The weights file is located at config/recommendation_weights.json
        and can be overridden via RECOMMENDATION_WEIGHTS_PATH env var.
        
        Returns:
            dict: Weights dictionary with keys like "skill", "level", etc.
        
        Raises:
            FileNotFoundError: If the weights config file doesn't exist
            ValueError: If the JSON is invalid or weights are malformed
        """
        weights_path = os.getenv(
            "RECOMMENDATION_WEIGHTS_PATH",
            Path(__file__).parent.parent / "config" / "recommendation_weights.json"
        )
        
        try:
            with open(weights_path, 'r', encoding='utf-8') as f:
                weights = json.load(f)
            
            # Validate that all expected keys exist
            expected_keys = {"skill", "level", "interest", "time"}
            if not expected_keys.issubset(weights.keys()):
                missing = expected_keys - set(weights.keys())
                raise ValueError(f"Missing required weight keys: {missing}")
            
            # Validate that all values are positive numbers
            for key, value in weights.items():
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError(f"Weight '{key}' must be a positive number, got {value}")
            
            return weights
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Recommendation weights config not found at {weights_path}. "
                "Please create config/recommendation_weights.json"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in recommendation weights config: {e}")


## Step 3: Add these lines at the end of the file (outside the Config class)

# Lazy-load weights to avoid file I/O on import
_RECOMMENDATION_WEIGHTS = None

def get_recommendation_weights():
    """
    Get recommendation scoring weights (cached).
    
    Weights are loaded once on first call and then cached.
    """
    global _RECOMMENDATION_WEIGHTS
    if _RECOMMENDATION_WEIGHTS is None:
        _RECOMMENDATION_WEIGHTS = Config.load_recommendation_weights()
    return _RECOMMENDATION_WEIGHTS

## Complete Updated config.py

# config.py
# Application configuration settings for DevPath.
#
# This module centralizes all configuration values that might change
# between environments (development, production, forks).

import os
import json
from pathlib import Path

class Config:
    """Base configuration class with sensible defaults."""
    
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
    
    @classmethod
    def load_recommendation_weights(cls):
        """
        Load recommendation scoring weights from config file.
        
        The weights file is located at config/recommendation_weights.json
        and can be overridden via RECOMMENDATION_WEIGHTS_PATH env var.
        
        Returns:
            dict: Weights dictionary with keys like "skill", "level", etc.
        
        Raises:
            FileNotFoundError: If the weights config file doesn't exist
            ValueError: If the JSON is invalid or weights are malformed
        """
        weights_path = os.getenv(
            "RECOMMENDATION_WEIGHTS_PATH",
            Path(__file__).parent.parent / "config" / "recommendation_weights.json"
        )
        
        try:
            with open(weights_path, 'r', encoding='utf-8') as f:
                weights = json.load(f)
            
            # Validate that all expected keys exist
            expected_keys = {"skill", "level", "interest", "time"}
            if not expected_keys.issubset(weights.keys()):
                missing = expected_keys - set(weights.keys())
                raise ValueError(f"Missing required weight keys: {missing}")
            
            # Validate that all values are positive numbers
            for key, value in weights.items():
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValueError(f"Weight '{key}' must be a positive number, got {value}")
            
            return weights
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Recommendation weights config not found at {weights_path}. "
                "Please create config/recommendation_weights.json"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in recommendation weights config: {e}")


# Lazy-load weights to avoid file I/O on import
_RECOMMENDATION_WEIGHTS = None

def get_recommendation_weights():
    """
    Get recommendation scoring weights (cached).
    
    Weights are loaded once on first call and then cached.
    """
    global _RECOMMENDATION_WEIGHTS
    if _RECOMMENDATION_WEIGHTS is None:
        _RECOMMENDATION_WEIGHTS = Config.load_recommendation_weights()
    return _RECOMMENDATION_WEIGHTS
