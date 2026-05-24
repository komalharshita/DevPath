# extensions.py
# Contains globally accessible extension instances to avoid circular dependencies.

from flask_caching import Cache

cache = Cache()
