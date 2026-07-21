# utils/portfolio_analyzer.py
#
# Portfolio Diversity Analyzer
# -----------------------------
# Looks at a user's completed projects and figures out which skill
# "domains" (Frontend, Backend, Testing, AI/ML, etc.) they've actually
# practiced, vs. which ones they keep skipping. Returns a diversity
# score plus targeted project recommendations for the gaps.

import re
from collections import OrderedDict

# Ordered so the dashboard always renders categories in a stable,
# predictable order (insertion order in Python 3.7+ dicts is preserved,
# OrderedDict just makes that intent explicit).
PROJECT_CATEGORIES = OrderedDict([
    ("Frontend", {
        "icon": "🎨",
        "keywords": ["react", "vue", "angular", "html", "css", "javascript",
                     "tailwind", "bootstrap", "frontend", "ui"],
    }),
    ("Backend", {
        "icon": "⚙️",
        "keywords": ["flask", "django", "express", "node", "spring",
                     "fastapi", "backend", "server"],
    }),
    ("Database", {
        "icon": "🗄️",
        "keywords": ["mysql", "mongodb", "postgresql", "sqlite", "firebase",
                     "database", "sql", "nosql"],
    }),
    ("Authentication", {
        "icon": "🔐",
        "keywords": ["jwt", "oauth", "login", "authentication", "auth",
                     "signup", "session"],
    }),
    ("API Integration", {
        "icon": "🔌",
        "keywords": ["api", "rest", "graphql", "axios", "fetch", "webhook"],
    }),
    ("Testing", {
        "icon": "🧪",
        "keywords": ["pytest", "jest", "testing", "unit test", "unittest",
                     "test coverage", "tdd"],
    }),
    ("Deployment", {
        "icon": "🚀",
        "keywords": ["docker", "vercel", "netlify", "aws", "render",
                     "heroku", "deployment", "deploy"],
    }),
    ("AI/ML", {
        "icon": "🤖",
        "keywords": ["machine learning", "tensorflow", "opencv", "ai", "ml",
                     "pytorch", "scikit", "nlp", "llm"],
    }),
    ("DevOps", {
        "icon": "🛠️",
        "keywords": ["kubernetes", "github actions", "jenkins", "ci/cd",
                     "ci-cd", "pipeline", "devops"],
    }),
    ("Real-time", {
        "icon": "💬",
        "keywords": ["socket", "websocket", "chat", "firebase realtime",
                     "real-time", "realtime", "live"],
    }),
])

# Suggested project for each domain, used when that domain is missing
# from the user's completed projects.
RECOMMENDATION_MAP = {
    "Frontend": "Create a Responsive Portfolio Website",
    "Backend": "Build a REST API using Flask",
    "Database": "Build a Full Stack CRUD Application",
    "Authentication": "Build a JWT Authentication System",
    "API Integration": "Build a Weather Dashboard using REST API",
    "Testing": "Build a Unit Testing Suite using PyTest",
    "Deployment": "Deploy a MERN Application using Docker",
    "AI/ML": "Create an Image Classification Project",
    "DevOps": "Create a CI/CD Pipeline with GitHub Actions",
    "Real-time": "Build a Chat Application using Socket.IO",
}

# Max number of recommendations to surface at once, so the dashboard
# isn't overwhelming when almost everything is missing.
MAX_RECOMMENDATIONS = 3


def _build_keyword_pattern(keywords):
    """Compile a single regex that matches any keyword as a whole word/phrase.

    Using \\b word boundaries prevents false positives like the keyword
    "ml" matching inside "html", or "ai" matching inside "email"/"daily" —
    both of which happened with naive substring (`keyword in text`) checks.
    """
    escaped = [re.escape(kw) for kw in keywords]
    pattern = r'\b(?:' + '|'.join(escaped) + r')\b'
    return re.compile(pattern, re.IGNORECASE)


for _category, _info in PROJECT_CATEGORIES.items():
    _info["pattern"] = _build_keyword_pattern(_info["keywords"])


def _project_text(project):
    """Flatten a project's searchable fields into one lowercase string."""
    return " ".join([
        project.get("title", "") or "",
        project.get("description", "") or "",
        " ".join(project.get("skills", []) or []),
        " ".join(project.get("tech_stack", []) or []),
        " ".join(project.get("features", []) or []),
    ]).lower()


def analyze_portfolio(projects):
    """
    Analyze a list of completed project dicts and return:
      - score:            int 0-100 diversity score
      - covered:           list[str] of domains the user has touched
      - missing:           list[str] of domains the user hasn't touched
      - categories:        ordered list of {name, icon, covered} for the UI
      - recommendations:   list of {category, icon, title} project ideas
                           that target the user's weakest areas
    """
    covered_categories = set()

    for project in projects or []:
        text = _project_text(project)
        for category, info in PROJECT_CATEGORIES.items():
            if category in covered_categories:
                continue
            if info["pattern"].search(text):
                covered_categories.add(category)

    total_categories = len(PROJECT_CATEGORIES)
    score = round((len(covered_categories) / total_categories) * 100) if total_categories else 0

    categories = [
        {
            "name": category,
            "icon": info["icon"],
            "covered": category in covered_categories,
        }
        for category, info in PROJECT_CATEGORIES.items()
    ]

    missing_categories = [c for c in PROJECT_CATEGORIES if c not in covered_categories]

    recommendations = [
        {
            "category": category,
            "icon": PROJECT_CATEGORIES[category]["icon"],
            "title": RECOMMENDATION_MAP[category],
        }
        for category in missing_categories
        if category in RECOMMENDATION_MAP
    ][:MAX_RECOMMENDATIONS]

    return {
        "score": score,
        "covered": sorted(covered_categories),
        "missing": missing_categories,
        "categories": categories,
        "recommendations": recommendations,
        "total_categories": total_categories,
        "covered_count": len(covered_categories),
    }