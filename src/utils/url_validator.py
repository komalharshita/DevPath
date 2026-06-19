# utils/url_validator.py
# Compatibility shim forwarding to services.url_validator_service
from services.url_validator_service import (
    is_valid_url,
    parse_resource,
    validate_resource,
    validate_resources,
)
