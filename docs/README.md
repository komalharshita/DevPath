# DevPath Documentation Portal

Welcome to the DevPath technical documentation suite. Whether you are an open-source contributor, architect, or developer exploring the API, you will find detailed guides and specifications below.

---

## 📚 Documentation Index

| Guide | Description | Target Audience |
|---|---|---|
| **[System Architecture](architecture.md)** | Detailed system components, Blueprint design, security model, and request lifecycles. | Contributors & Maintainers |
| **[REST API Reference](api_reference.md)** | Complete endpoint specifications, request payloads, schemas, and responses. | Integrators & Frontend Developers |
| **[Contribution Guide](contribution_guide.md)** | Step-by-step development setup, branch naming, testing, and PR guidelines. | GSSoC & Open Source Contributors |
| **[Project Overview](project_overview.md)** | Mission, problem statement, and algorithm scoring design. | All Developers |
| **[Security Policy](security.md)** | Security architecture, vulnerability reporting, and best practices. | Security Researchers & Deployers |
| **[Frequently Asked Questions](faq.md)** | Common troubleshooting tips and implementation questions. | General |

---

## 🚀 Quick Technical Summary

- **Backend**: Python 3.8+ & Flask 3.1
- **Database**: SQLite with SQLAlchemy ORM (auto-seeded from `data/projects.json`)
- **Authentication**: Authlib (OAuth 2.0 with GitHub integration)
- **Frontend**: Vanilla JavaScript (ES6+), Semantic HTML5, Glassmorphism CSS design system
- **Security**: Strict CSP, Flask-WTF CSRF tokens, secure session cookie policies
- **Testing**: Automated `pytest` suite with **660+ passing test cases**

---

## 🛠️ Running Locally

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start development server
PORT=5001 python src/app.py
```

Then visit **http://localhost:5001** in your browser.
