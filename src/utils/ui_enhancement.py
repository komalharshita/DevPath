"""UI/UX enhancements including navigation, filtering, and accessibility."""

from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class AccessibilityLevel(Enum):
    """WCAG accessibility levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class UIEnhancementManager:
    """Manages UI improvements, filtering, and accessibility features."""

    def __init__(self):
        self.filters: Dict[str, List[str]] = {}
        self.navigation_structure: Dict = {}
        self.accessibility_features: Dict[str, bool] = {}
        self.user_preferences: Dict[str, Dict] = {}

    def add_filter_option(self, category: str, options: List[str]):
        """Add filter options for a category."""
        self.filters[category] = options

    def get_available_filters(self) -> Dict[str, List[str]]:
        """Get all available filter options."""
        return self.filters.copy()

    def apply_filters(
        self, items: List[Dict], filter_config: Dict
    ) -> List[Dict]:
        """Apply multiple filters to items."""
        filtered = items

        for key, value in filter_config.items():
            if isinstance(value, list):
                filtered = [
                    item for item in filtered if item.get(key) in value
                ]
            else:
                filtered = [
                    item for item in filtered if item.get(key) == value
                ]

        return filtered

    def search_items(self, items: List[Dict], query: str, fields: List[str]) -> List[Dict]:
        """Search items across specified fields."""
        query_lower = query.lower()
        results = []

        for item in items:
            for field in fields:
                if field in item:
                    value = str(item[field]).lower()
                    if query_lower in value:
                        results.append(item)
                        break

        return results

    def build_navigation_menu(self) -> Dict:
        """Build improved navigation menu structure."""
        return {
            "primary": [
                {"label": "Home", "url": "/", "icon": "home"},
                {"label": "Browse", "url": "/browse", "icon": "search"},
                {"label": "My Learning", "url": "/my-learning", "icon": "book"},
                {"label": "Community", "url": "/community", "icon": "users"},
            ],
            "secondary": [
                {"label": "Resources", "url": "/resources", "icon": "link"},
                {"label": "Settings", "url": "/settings", "icon": "gear"},
            ],
        }

    def enable_accessibility_feature(self, feature: str) -> bool:
        """Enable an accessibility feature."""
        features = {
            "dark_mode": True,
            "high_contrast": True,
            "large_text": True,
            "text_spacing": True,
            "keyboard_navigation": True,
            "screen_reader": True,
            "captions": True,
            "focus_indicator": True,
        }
        self.accessibility_features[feature] = features.get(feature, False)
        return self.accessibility_features[feature]

    def get_accessibility_status(self) -> Dict:
        """Get accessibility feature status."""
        return {
            "wcag_level": AccessibilityLevel.AA.value,
            "features_enabled": self.accessibility_features,
            "compliance": True,
        }

    def set_user_ui_preference(
        self, user_id: str, preferences: Dict
    ) -> Dict:
        """Set user UI preferences."""
        self.user_preferences[user_id] = {
            "theme": preferences.get("theme", "light"),
            "language": preferences.get("language", "en"),
            "font_size": preferences.get("font_size", "normal"),
            "layout": preferences.get("layout", "compact"),
        }
        return self.user_preferences[user_id]

    def get_user_ui_preference(self, user_id: str) -> Dict:
        """Get user's UI preferences."""
        return self.user_preferences.get(user_id, {})

    def get_ui_guidance(self, page: str) -> Dict:
        """Get in-app guidance for a page."""
        guidance_map = {
            "home": "Welcome! Start by selecting a skill and difficulty level.",
            "browse": "Use filters to find projects matching your interests.",
            "my-learning": "Track your learning progress here.",
            "community": "Ask questions and share knowledge with peers.",
        }
        return {"page": page, "guidance": guidance_map.get(page, "")}

    def track_navigation_flow(self, user_id: str, from_page: str, to_page: str):
        """Track user navigation for UX improvements."""
        return {
            "user_id": user_id,
            "from": from_page,
            "to": to_page,
            "timestamp": str(datetime.utcnow()),
        }
