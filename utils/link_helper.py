# utils/link_helper.py
# Reusable helper to parse and standardize external link handling.

import re

def parse_external_link(resource):
    """
    Safely parses a resource string which might contain an external URL.
    
    Supports:
      - "Label: https://url"
      - "Label - https://url"
      - "https://url" (plain URL)
      - Plain text (no URL)
      
    Returns a dict:
      {
        "label": str,
        "url": str or None,
        "is_link": bool
      }
    """
    if not resource:
        return {"label": "", "url": None, "is_link": False}

    resource_str = str(resource).strip()
    
    # Regex to find a standard http/https URL
    url_match = re.search(r'https?://[^\s]+', resource_str)
    if not url_match:
        return {"label": resource_str, "url": None, "is_link": False}
    
    url = url_match.group(0)
    
    # The label is whatever is before the URL, stripped of colons, dashes, and spaces
    label_part = resource_str[:url_match.start()].strip()
    if label_part:
        # Remove trailing colons, dashes, or spaces
        label = re.sub(r'[:\-–—\s]+$', '', label_part).strip()
    else:
        label = url
        
    return {
        "label": label,
        "url": url,
        "is_link": True
    }
