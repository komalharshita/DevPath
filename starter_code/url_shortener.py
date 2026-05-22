"""
url_shortener.py
================
Project:    URL Shortener
Difficulty: Intermediate
Skills:     Python, Flask, HTML forms, JSON, secrets module
Time:       High (a week or more)

What you will build:
    A full-stack web app that takes long URLs and generates short codes.
    Paste a link, get a short URL back. Visiting the short URL redirects
    you to the original. A dashboard shows all links and click counts.

How to run:
    pip install flask
    python url_shortener.py
    Open http://127.0.0.1:5000 in your browser.

Learning goals:
    - Building a full-stack Flask application (backend + frontend together)
    - Generating secure random short codes with the secrets module
    - Storing and retrieving key-value data in a JSON file
    - Implementing HTTP redirects with Flask
    - Rendering dynamic HTML with Jinja2 templates
    - Tracking simple click analytics

URL data structure (stored in urls.json):
    {
        "abc123": {
            "original_url":  "https://www.example.com/very/long/path",
            "short_code":    "abc123",
            "clicks":        14,
            "created_at":    "2024-03-01T10:00:00"
        }
    }

Roadmap:
    Step 1:  Run the server and visit the homepage — the HTML renders already
    Step 2:  Complete generate_short_code() using secrets.token_urlsafe
    Step 3:  Complete is_valid_url() to check for http:// or https://
    Step 4:  Complete shorten() to create and store a new short URL
    Step 5:  Complete redirect_to_url() to look up a code and redirect
    Step 6:  Complete increment_clicks() to count each visit
    Step 7:  Complete get_all_links() to return data for the dashboard
    Step 8:  Complete delete_link() to remove a short URL
"""

import json
import os
import secrets
from datetime import datetime

from flask import Flask, redirect, render_template_string, request, jsonify, abort

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# JSON file that stores all short URL mappings
DATA_FILE = "urls.json"

# Length of the generated short code (characters)
CODE_LENGTH = 6

# Base URL used to build the full short link shown to users
# Change this to your deployed domain when you go live
BASE_URL = "http://127.0.0.1:5000"


# ---------------------------------------------------------------------------
# HTML templates — already complete, no changes needed
# The templates are embedded here to keep the project single-file.
# In a larger project you would move these to a templates/ folder.
# ---------------------------------------------------------------------------

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background: #f0f2ff;
            color: #1a1a2e;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 20px;
        }
        h1 { font-size: 2rem; margin-bottom: 8px; color: #2335c2; }
        p.sub { color: #6b7280; margin-bottom: 36px; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 36px;
            width: 100%;
            max-width: 560px;
            box-shadow: 0 4px 20px rgba(35,53,194,0.1);
            margin-bottom: 24px;
        }
        input[type=text] {
            width: 100%;
            padding: 12px 14px;
            border: 1.5px solid #e5e7eb;
            border-radius: 8px;
            font-size: 0.95rem;
            margin-bottom: 14px;
        }
        input[type=text]:focus { outline: none; border-color: #4f6ef7; }
        button {
            width: 100%;
            padding: 13px;
            background: linear-gradient(90deg, #2335c2, #7c3aed);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
        }
        .result {
            background: #eef1ff;
            border-radius: 8px;
            padding: 14px 18px;
            margin-top: 16px;
            display: none;
        }
        .result a { color: #2335c2; font-weight: 600; word-break: break-all; }
        .result .copy-btn {
            background: #2335c2;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 0.84rem;
            cursor: pointer;
            margin-left: 8px;
            width: auto;
        }
        table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
        th { text-align: left; padding: 8px 12px; background: #f3f4f6;
             font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; }
        td { padding: 10px 12px; border-top: 1px solid #f3f4f6; word-break: break-all; }
        tr:hover td { background: #f9fafb; }
        .clicks { font-weight: 600; color: #2335c2; }
        .del-btn {
            background: #fee2e2; color: #dc2626; border: none;
            border-radius: 4px; padding: 4px 10px; cursor: pointer;
            font-size: 0.78rem; width: auto;
        }
        .error { color: #dc2626; margin-top: 10px; font-size: 0.88rem; }
    </style>
</head>
<body>
    <h1>URL Shortener</h1>
    <p class="sub">Paste a long link. Get a short one.</p>

    <div class="card">
        <input type="text" id="url-input" placeholder="https://your-long-url.com/path/to/page" />
        <button onclick="shortenUrl()">Shorten URL</button>
        <p class="error" id="error-msg"></p>
        <div class="result" id="result-box">
            <strong>Your short link:</strong><br>
            <a id="short-link" href="#" target="_blank"></a>
            <button class="copy-btn" onclick="copyLink()">Copy</button>
        </div>
    </div>

    {% if links %}
    <div class="card">
        <h3 style="margin-bottom:16px;">All Links</h3>
        <table>
            <thead>
                <tr>
                    <th>Short Code</th>
                    <th>Original URL</th>
                    <th>Clicks</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
            {% for code, data in links.items() %}
                <tr>
                    <td><a href="/{{ code }}" target="_blank">{{ code }}</a></td>
                    <td style="max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                        {{ data.original_url }}
                    </td>
                    <td class="clicks">{{ data.clicks }}</td>
                    <td>
                        <button class="del-btn"
                            onclick="deleteLink('{{ code }}')">Delete</button>
                    </td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}

    <script>
        function shortenUrl() {
            var url = document.getElementById('url-input').value.trim();
            document.getElementById('error-msg').textContent = '';
            document.getElementById('result-box').style.display = 'none';

            if (!url) {
                document.getElementById('error-msg').textContent = 'Please enter a URL.';
                return;
            }

            fetch('/shorten', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.error) {
                    document.getElementById('error-msg').textContent = data.error;
                    return;
                }
                var link = document.getElementById('short-link');
                link.href = data.short_url;
                link.textContent = data.short_url;
                document.getElementById('result-box').style.display = 'block';
                setTimeout(function() { location.reload(); }, 1200);
            });
        }

        function copyLink() {
            var text = document.getElementById('short-link').textContent;
            navigator.clipboard.writeText(text);
        }

        function deleteLink(code) {
            if (!confirm('Delete this short link?')) return;
            fetch('/delete/' + code, { method: 'DELETE' })
            .then(function() { location.reload(); });
        }
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Data helpers — already complete
# ---------------------------------------------------------------------------

def load_urls():
    """
    Load the URL mapping dictionary from the JSON file.

    Returns:
        dict: Keys are short codes, values are URL data dicts.
              Returns {} if the file does not exist yet.
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_urls(urls):
    """
    Save the full URL mapping dictionary to the JSON file.

    Args:
        urls (dict): The complete mapping of short codes to URL data.
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2)


# ---------------------------------------------------------------------------
# Core logic — complete the TODOs below
# ---------------------------------------------------------------------------

def generate_short_code():
    """
    Generate a random, URL-safe short code.

    Returns:
        str: A random string of CODE_LENGTH characters using URL-safe
             Base64 characters (letters, numbers, hyphens, underscores).

    TODO:
        1. Use secrets.token_urlsafe() to generate a random string.
           token_urlsafe(n) generates approximately n bytes encoded as
           Base64, resulting in a string longer than n characters.
        2. Slice the result to exactly CODE_LENGTH characters: [:CODE_LENGTH]
        3. Return the sliced string.

    Example:
        generate_short_code()  ->  "aB3xKz"
    """
    # --- Write your code here ---

    pass


def is_valid_url(url):
    """
    Check whether a URL string starts with http:// or https://.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL starts with http:// or https://, False otherwise.

    TODO:
        Use str.startswith() with a tuple of valid prefixes.
        Return True or False based on the check.

    Examples:
        is_valid_url("https://example.com")  ->  True
        is_valid_url("example.com")          ->  False
        is_valid_url("ftp://files.org")      ->  False
    """
    # --- Write your code here ---

    return False


def increment_clicks(short_code):
    """
    Increase the click counter for a short code by 1 and save.

    Args:
        short_code (str): The short code whose click count should increase.

    TODO:
        1. Call load_urls() to get the current mapping.
        2. Check that short_code exists in the mapping.
        3. Increment urls[short_code]["clicks"] by 1.
        4. Call save_urls(urls) to persist the change.
    """
    # --- Write your code here ---

    pass


# ---------------------------------------------------------------------------
# Routes — complete the TODOs in each handler
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    """
    GET /
    Render the homepage with the shorten form and all existing links.

    TODO:
        1. Call load_urls() to get all current links.
        2. Pass the links dict to render_template_string().
        3. Return the rendered page.

    Example:
        return render_template_string(HOME_TEMPLATE, links=all_links)
    """
    # --- Write your code here ---

    pass


@app.route("/shorten", methods=["POST"])
def shorten():
    """
    POST /shorten
    Create a new short URL from the JSON request body.

    Expected body:
        { "url": "https://example.com/long/path" }

    Response: 200 OK
        {
            "short_url":  "http://127.0.0.1:5000/aB3xKz",
            "short_code": "aB3xKz",
            "original":   "https://example.com/long/path"
        }

    Error: 400
        { "error": "..." }

    TODO:
        1. Read the JSON body: data = request.get_json()
        2. Extract the "url" field. Return 400 if missing or blank.
        3. Call is_valid_url(). Return 400 if the URL is not valid.
        4. Generate a unique short code with generate_short_code().
           Make sure the code does not already exist in the loaded URLs
           (generate again if it does — collision is extremely unlikely
           but worth handling).
        5. Build the URL data dict:
               {
                   "original_url": url,
                   "short_code":   code,
                   "clicks":       0,
                   "created_at":   datetime.utcnow().isoformat()
               }
        6. Load the current URLs, add the new entry, save.
        7. Return the short URL: f"{BASE_URL}/{code}"
    """
    # --- Write your code here ---

    pass


@app.route("/<short_code>", methods=["GET"])
def redirect_to_url(short_code):
    """
    GET /<short_code>
    Look up the short code and redirect the visitor to the original URL.

    If the code does not exist, return a 404 response.

    TODO:
        1. Call load_urls() and look up short_code as a key.
        2. If the code is not in the dict, abort(404).
        3. Call increment_clicks(short_code) to record the visit.
        4. Use redirect(urls[short_code]["original_url"]) to send the browser
           to the original URL.
           Flask import: from flask import redirect
    """
    # --- Write your code here ---

    pass


@app.route("/delete/<short_code>", methods=["DELETE"])
def delete_link(short_code):
    """
    DELETE /delete/<short_code>
    Remove a short URL from the mapping permanently.

    Response: 200   -> { "message": "Deleted." }
    Response: 404   -> { "error": "Short code not found." }

    TODO:
        1. Load the current URLs.
        2. If the short_code is not present, return 404.
        3. Delete the entry: del urls[short_code]
        4. Save the updated mapping.
        5. Return { "message": "Deleted." }, 200
    """
    # --- Write your code here ---

    pass


@app.route("/stats/<short_code>", methods=["GET"])
def get_stats(short_code):
    """
    GET /stats/<short_code>
    Return the stats for one short URL as JSON.

    Response: 200   -> { "short_code": ..., "clicks": ..., ... }
    Response: 404   -> { "error": "Short code not found." }

    TODO:
        1. Load URLs and look up the code.
        2. Return 404 if not found.
        3. Return the full URL data dict as JSON with status 200.
    """
    # --- Write your code here ---

    pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("URL Shortener starting...")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    print(f"Base URL:  {BASE_URL}")
    print("Open http://127.0.0.1:5000 in your browser.\n")
    app.run(debug=True)
