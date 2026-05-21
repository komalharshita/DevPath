# utils/analytics.py
# Simple utility to log search patterns and return popular queries/trending terms.

import json
import os
from datetime import datetime

ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "search_analytics.json")
MAX_LOG_ENTRIES = 200

# Default trending items to display if history is empty
DEFAULT_TRENDING = ["Python", "Flask", "React", "pandas", "Machine Learning"]


def log_search_query(q, filters, result_count):
    """
    Log the search parameters, filters, and match count to a JSON file.
    Caps history to MAX_LOG_ENTRIES to prevent unbounded growth.
    """
    # Build log entry
    entry = {
        "q": q,
        "filters": {k: v for k, v in filters.items() if v},  # Only log non-empty filters
        "result_count": result_count,
        "timestamp": datetime.now().isoformat()
    }

    logs = []
    
    # Read existing logs
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    logs = []
        except (json.JSONDecodeError, IOError):
            logs = []

    # Insert at the beginning of the list
    logs.insert(0, entry)

    # Cap list size
    logs = logs[:MAX_LOG_ENTRIES]

    # Save to file
    try:
        # Create data directory if it somehow doesn't exist
        os.makedirs(os.path.dirname(ANALYTICS_FILE), exist_ok=True)
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except IOError as e:
        print(f"Failed to write search analytics: {e}")


def get_trending_searches(limit=5):
    """
    Aggregate search history to find the most frequent queries and tags.
    If search history is sparse, falls back to DEFAULT_TRENDING.
    """
    if not os.path.exists(ANALYTICS_FILE):
        return DEFAULT_TRENDING[:limit]

    try:
        with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
            if not logs or not isinstance(logs, list):
                return DEFAULT_TRENDING[:limit]
    except (json.JSONDecodeError, IOError):
        return DEFAULT_TRENDING[:limit]

    # Aggregate counts of query terms and tags used
    frequency = {}

    for entry in logs:
        # Check text query
        q = entry.get("q", "").strip().lower()
        if q:
            frequency[q] = frequency.get(q, 0) + 2  # Higher weight for typed query terms

        # Check filter elements
        filters = entry.get("filters", {})
        
        # Add tech stack queries
        techs = filters.get("tech_stack", "")
        if techs:
            for t in techs.split(","):
                t_clean = t.strip().lower()
                if t_clean:
                    frequency[t_clean] = frequency.get(t_clean, 0) + 1
                    
        # Add skill queries
        skills = filters.get("skills", "")
        if skills:
            for s in skills.split(","):
                s_clean = s.strip().lower()
                if s_clean:
                    frequency[s_clean] = frequency.get(s_clean, 0) + 1

    if not frequency:
        return DEFAULT_TRENDING[:limit]

    # Sort items by frequency count descending
    sorted_items = sorted(frequency.items(), key=lambda item: item[1], reverse=True)

    # Format properly (Title Case or original name matching default list)
    trending = []
    for term, _ in sorted_items:
        # Map back to standard capitalized terms if matched to make them look beautiful
        mapped = term.capitalize()
        if mapped.lower() in [d.lower() for d in DEFAULT_TRENDING]:
            # Use original exact case from defaults
            mapped = next(d for d in DEFAULT_TRENDING if d.lower() == mapped.lower())
        
        # Specific casing rules
        if mapped.lower() == "javascript":
            mapped = "JavaScript"
        elif mapped.lower() == "react":
            mapped = "React"
        elif mapped.lower() == "html":
            mapped = "HTML"
        elif mapped.lower() == "css":
            mapped = "CSS"
        elif mapped.lower() == "ml" or mapped.lower() == "machine learning":
            mapped = "Machine Learning"

        if mapped not in trending:
            trending.append(mapped)

    # Combine with default terms if we have fewer than limit
    for item in DEFAULT_TRENDING:
        if len(trending) >= limit:
            break
        if item not in trending:
            trending.append(item)

    return trending[:limit]
