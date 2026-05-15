"""
Tourism Website
===========

Project: Tourism Website
Difficulty: Advanced
Skills:     Python, Flask, JSON, HTTP methods,HTML,CSS,JAvascript
Time:  High

What you will build:
This tourism website project is a full-stack web application where
users can explore different tourist destinations, view detailed information about each place,
and read ratings and reviews shared by other visitors. The platform is designed to help travelers
discover popular locations before planning their trips. Each destination listing includes images, descriptions, location details, ratings, and user reviews, 
creating an interactive and informative experience for users.
Visitors can also submit their own reviews and ratings after exploring a destination, allowing the website to build a community-driven recommendation system.
The website will have a frontend developed using HTML, CSS, and JavaScript to create a responsive and visually attractive user interface, while the backend will be built using Python Flask to handle routing, 
authentication, database operations, and review management.
A database such as SQLite or MySQL will store user information, 
destination listings, ratings, and reviews.
The platform will also include an admin panel where administrators can add new tourist destinations,
upload images, edit existing listings, and manage reviews. This project helps in learning full-stack web development concepts such as frontend design, 
backend APIs, database management, authentication, CRUD operations, and user interaction systems, making it a strong intermediate-to-advanced development project for building real-world web application skills.

How to run:
pip install flask flask_sqlalchemy flask_login

Create folders for css,js
templates/
static/

Then test your endpoints with curl or  postman:
 curl http://127.0.0.1:5000/tasks

Then run the app using app.py

Learning goals:
- Understand the basics of web development using Flask.
- Learn how to create a RESTful API with Flask.
- Implement CRUD operations for managing tourist destinations and reviews.
- Use a database to store and retrieve data.
- Implement user authentication and authorization.
- Create a responsive and user-friendly frontend using HTML, CSS, and JavaScript.

Rest endpoint reference:
- GET /destinations: Retrieve a list of all tourist destinations.
- GET /destinations/<id>: Retrieve detailed information about a specific destination by its ID.
- POST /destinations: Add a new tourist destination (admin only).
- PUT /destinations/<id>: Update information about a specific destination (admin only).
- DELETE /destinations/<id>: Remove a specific destination from the database (admin only).
- POST /destinations/<id>/reviews: Submit a new review for a specific destination.  

Roadmap:
1. Set up the Flask application and configure the database.
2. Create models for users, destinations, and reviews.
3. Implement user authentication and authorization.
4. Develop RESTful API endpoints for managing destinations and reviews.
5. Create frontend templates for displaying destinations and reviews.
6. Implement the admin panel for managing destinations and reviews. 
7.Test the application using tools like Postman or curl to ensure all endpoints work correctly.
8. Deploy the application to a hosting service like Vercel or render for public access.

"""
import json
import os
import uuid
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_FILE = "destinations.json"

VALID_CATEGORIES = [
    "beach",
    "mountain",
    "historical",
    "adventure",
    "religious",
    "nature"
]

VALID_RATINGS = [1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
# Data Helpers
# ---------------------------------------------------------------------------

def load_destinations():

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def save_destinations(destinations):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(destinations, f, indent=2)


def find_destination_by_id(destinations, destination_id):

    for destination in destinations:
        if destination["id"] == destination_id:
            return destination

    return None


def generate_id():
    return str(uuid.uuid4())


def current_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():

    destinations = load_destinations()

    return jsonify({
        "status": "running",
        "message": "Tourism Website API Running Successfully",
        "total_destinations": len(destinations)
    }), 200


# ---------------------------------------------------------------------------
# Get All Destinations
# ---------------------------------------------------------------------------

@app.route("/destinations", methods=["GET"])
def get_destinations():

    destinations = load_destinations()

    category = request.args.get("category")

    if category:
        destinations = [
            d for d in destinations
            if d["category"] == category
        ]

    return jsonify({
        "destinations": destinations,
        "count": len(destinations)
    }), 200


# ---------------------------------------------------------------------------
# Add Destination (Admin)
# ---------------------------------------------------------------------------

@app.route("/destinations", methods=["POST"])
def create_destination():

    data = request.get_json()

    if data is None:
        return jsonify({
            "error": "Request body must be JSON."
        }), 400

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    location = data.get("location", "").strip()
    image = data.get("image", "").strip()

    category = data.get("category", "nature")

    if not title:
        return jsonify({
            "error": "Title is required."
        }), 400

    if category not in VALID_CATEGORIES:
        return jsonify({
            "error": f"Invalid category. Use {VALID_CATEGORIES}"
        }), 400

    new_destination = {
        "id": generate_id(),
        "title": title,
        "description": description,
        "location": location,
        "image": image,
        "category": category,
        "reviews": [],
        "created_at": current_timestamp()
    }

    destinations = load_destinations()

    destinations.append(new_destination)

    save_destinations(destinations)

    return jsonify({
        "message": "Destination created successfully.",
        "destination": new_destination
    }), 201


# ---------------------------------------------------------------------------
# Get Single Destination
# ---------------------------------------------------------------------------

@app.route("/destinations/<destination_id>", methods=["GET"])
def get_destination(destination_id):

    destinations = load_destinations()

    destination = find_destination_by_id(
        destinations,
        destination_id
    )

    if destination is None:
        return jsonify({
            "error": "Destination not found."
        }), 404

    return jsonify({
        "destination": destination
    }), 200


# ---------------------------------------------------------------------------
# Update Destination
# ---------------------------------------------------------------------------

@app.route("/destinations/<destination_id>", methods=["PUT"])
def update_destination(destination_id):

    destinations = load_destinations()

    destination = find_destination_by_id(
        destinations,
        destination_id
    )

    if destination is None:
        return jsonify({
            "error": "Destination not found."
        }), 404

    data = request.get_json()

    if data is None:
        return jsonify({
            "error": "Request body must be JSON."
        }), 400

    if "title" in data:
        destination["title"] = data["title"]

    if "description" in data:
        destination["description"] = data["description"]

    if "location" in data:
        destination["location"] = data["location"]

    if "image" in data:
        destination["image"] = data["image"]

    if "category" in data:

        if data["category"] not in VALID_CATEGORIES:
            return jsonify({
                "error": f"Invalid category. Use {VALID_CATEGORIES}"
            }), 400

        destination["category"] = data["category"]

    destination["updated_at"] = current_timestamp()

    save_destinations(destinations)

    return jsonify({
        "message": "Destination updated successfully.",
        "destination": destination
    }), 200


# ---------------------------------------------------------------------------
# Delete Destination
# ---------------------------------------------------------------------------

@app.route("/destinations/<destination_id>", methods=["DELETE"])
def delete_destination(destination_id):

    destinations = load_destinations()

    destination = find_destination_by_id(
        destinations,
        destination_id
    )

    if destination is None:
        return jsonify({
            "error": "Destination not found."
        }), 404

    destinations = [
        d for d in destinations
        if d["id"] != destination_id
    ]

    save_destinations(destinations)

    return jsonify({
        "message": "Destination deleted successfully."
    }), 200


# ---------------------------------------------------------------------------
# Add Review
# ---------------------------------------------------------------------------

@app.route("/destinations/<destination_id>/reviews", methods=["POST"])
def add_review(destination_id):

    destinations = load_destinations()

    destination = find_destination_by_id(
        destinations,
        destination_id
    )

    if destination is None:
        return jsonify({
            "error": "Destination not found."
        }), 404

    data = request.get_json()

    if data is None:
        return jsonify({
            "error": "Request body must be JSON."
        }), 400

    username = data.get("username", "").strip()
    comment = data.get("comment", "").strip()
    rating = data.get("rating")

    if not username:
        return jsonify({
            "error": "Username is required."
        }), 400

    if not comment:
        return jsonify({
            "error": "Comment is required."
        }), 400

    if rating not in VALID_RATINGS:
        return jsonify({
            "error": "Rating must be between 1 and 5."
        }), 400

    review = {
        "id": generate_id(),
        "username": username,
        "comment": comment,
        "rating": rating,
        "created_at": current_timestamp()
    }

    destination["reviews"].append(review)

    save_destinations(destinations)

    return jsonify({
        "message": "Review added successfully.",
        "review": review
    }), 201


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error": "Endpoint not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        "error": "Method not allowed."
    }), 405


# ---------------------------------------------------------------------------
# Run Server
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("Tourism Website API Starting...")
    print(f"Data File: {os.path.abspath(DATA_FILE)}")
    print("Visit: http://127.0.0.1:5000")
    print("Press CTRL + C to stop.\n")

    app.run(debug=True)