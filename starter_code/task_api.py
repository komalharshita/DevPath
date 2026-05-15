"""
task_api.py
===========
Project:    Task Manager REST API
Difficulty: Intermediate
Skills:     Python, Flask, JSON, HTTP methods, REST design
Time:       Medium (a weekend)

What you will build:
    A RESTful API built with Flask that lets clients create, read, update,
    and delete tasks. Each task has a title, priority, status, and unique ID.
    Data is persisted to a JSON file between server restarts.

How to run:
    pip install flask
    python task_api.py

Then test your endpoints with curl or Postman:
    curl http://127.0.0.1:5000/tasks
    curl -X POST http://127.0.0.1:5000/tasks \
         -H "Content-Type: application/json" \
         -d '{"title": "Buy groceries", "priority": "medium"}'

Learning goals:
    - Designing and implementing REST API endpoints
    - Handling HTTP GET, POST, PUT, DELETE methods in Flask
    - Returning JSON responses with appropriate status codes
    - Persisting data to a JSON file
    - Validating request input and returning helpful error messages

REST endpoint reference:
    GET    /tasks              List all tasks (optional ?status= filter)
    POST   /tasks              Create a new task
    GET    /tasks/<id>         Get one task by ID
    PUT    /tasks/<id>         Update a task's title, priority, or status
    DELETE /tasks/<id>         Delete a task permanently

Roadmap:
    Step 1:  Run the server and confirm it starts without errors
    Step 2:  Complete get_tasks() — return all tasks as JSON
    Step 3:  Complete create_task() — validate input, generate ID, save
    Step 4:  Complete get_task() — return one task or 404
    Step 5:  Complete update_task() — update allowed fields and save
    Step 6:  Complete delete_task() — remove task by ID and save
    Step 7:  Test every endpoint with Postman or curl
    Step 8:  Add the status filter to get_tasks() (?status=pending)
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

# JSON file that stores all tasks between restarts
DATA_FILE = "tasks.json"

# Valid values for task status and priority fields
VALID_STATUSES = ["pending", "in_progress", "done"]
VALID_PRIORITIES = ["low", "medium", "high"]


# ---------------------------------------------------------------------------
# Data helpers — already complete
# ---------------------------------------------------------------------------

def load_tasks():
    """
    Read and return the list of all tasks from the JSON file.

    Returns:
        list[dict]: All task records. Returns [] if the file does not exist.

    Each task dict has this shape:
        {
            "id":         "a3f1...",          (unique UUID string)
            "title":      "Buy groceries",
            "status":     "pending",          (pending / in_progress / done)
            "priority":   "medium",           (low / medium / high)
            "created_at": "2024-03-01T10:00"
        }
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    """
    Write the full tasks list to the JSON file, overwriting any previous data.

    Args:
        tasks (list[dict]): The complete list of task records to save.
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def find_task_by_id(tasks, task_id):
    """
    Search for a task by its unique ID string.

    Args:
        tasks (list[dict]): The full task list.
        task_id (str):      The UUID string to search for.

    Returns:
        dict | None: The matching task dict, or None if not found.
    """
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def generate_id():
    """Return a new unique ID string using uuid4."""
    return str(uuid.uuid4())


def current_timestamp():
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# API Routes — complete the TODO in each handler
# ---------------------------------------------------------------------------

@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    GET /tasks
    Return all tasks as a JSON array.

    Optional query parameter:
        ?status=pending       Return only tasks with that status value.
        ?status=done          Return only completed tasks.

    Response: 200 OK
        {
            "tasks": [...],
            "count": 3
        }

    TODO:
        1. Call load_tasks() to get the full list.
        2. Check if request.args.get("status") was provided.
           If it was, filter the list to tasks where task["status"]
           matches the requested value.
        3. Return jsonify({"tasks": tasks, "count": len(tasks)}), 200
    """
    # --- Write your code here ---

    pass


@app.route("/tasks", methods=["POST"])
def create_task():
    """
    POST /tasks
    Create a new task from the JSON request body.

    Required body field:
        title (str): The task description. Must not be empty.

    Optional body fields:
        priority (str): "low", "medium", or "high". Defaults to "medium".
        status (str):   Initial status. Defaults to "pending".

    Response: 201 Created
        {
            "message": "Task created.",
            "task": { ...the new task... }
        }

    Error responses:
        400 — missing or empty title
        400 — invalid priority or status value

    TODO:
        1. Read the JSON body: data = request.get_json()
           If data is None, return a 400 error.
        2. Extract title from data. If it is missing or blank, return 400.
        3. Extract priority (default "medium") and status (default "pending").
        4. Validate priority against VALID_PRIORITIES. Return 400 if invalid.
        5. Validate status against VALID_STATUSES. Return 400 if invalid.
        6. Build the new task dict:
               {
                   "id":         generate_id(),
                   "title":      title,
                   "status":     status,
                   "priority":   priority,
                   "created_at": current_timestamp()
               }
        7. Load the current tasks list, append the new task, save.
        8. Return jsonify({"message": "Task created.", "task": new_task}), 201

    Example request body:
        {"title": "Buy groceries", "priority": "high"}
    """
    # --- Write your code here ---

    pass


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    """
    GET /tasks/<task_id>
    Return one task by its UUID.

    Response: 200 OK     -> {"task": {...}}
    Response: 404        -> {"error": "Task not found."}

    TODO:
        1. Call load_tasks() and then find_task_by_id(tasks, task_id).
        2. If the task is None, return jsonify({"error": "Task not found."}), 404
        3. Otherwise return jsonify({"task": task}), 200
    """
    # --- Write your code here ---

    pass


@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    """
    PUT /tasks/<task_id>
    Update one or more fields of an existing task.

    Updateable fields:
        title (str):    New task description. Must not be empty if provided.
        priority (str): Must be one of VALID_PRIORITIES if provided.
        status (str):   Must be one of VALID_STATUSES if provided.

    Response: 200 OK     -> {"message": "Task updated.", "task": {...}}
    Response: 404        -> {"error": "Task not found."}
    Response: 400        -> {"error": "...validation message..."}

    TODO:
        1. Load tasks, find the task by task_id. Return 404 if not found.
        2. Read the JSON body. Return 400 if body is missing.
        3. For each updateable field (title, priority, status):
             - Check if it is present in the body.
             - Validate its value.
             - Update task[field] = new_value.
        4. Add "updated_at": current_timestamp() to the task dict.
        5. Save the updated tasks list.
        6. Return the updated task with status 200.
    """
    # --- Write your code here ---

    pass


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    DELETE /tasks/<task_id>
    Permanently remove a task.

    Response: 200 OK     -> {"message": "Task deleted."}
    Response: 404        -> {"error": "Task not found."}

    TODO:
        1. Load tasks, find the task by task_id. Return 404 if not found.
        2. Remove the task from the list:
               tasks = [t for t in tasks if t["id"] != task_id]
        3. Save the updated list.
        4. Return jsonify({"message": "Task deleted."}), 200
    """
    # --- Write your code here ---

    pass


# ---------------------------------------------------------------------------
# Health check — already complete, no changes needed
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def health_check():
    """
    GET /
    A simple health-check endpoint that confirms the API is running.
    """
    tasks = load_tasks()
    return jsonify({
        "status": "running",
        "message": "Task Manager API is online.",
        "total_tasks": len(tasks),
        "endpoints": {
            "list_tasks":   "GET  /tasks",
            "create_task":  "POST /tasks",
            "get_task":     "GET  /tasks/<id>",
            "update_task":  "PUT  /tasks/<id>",
            "delete_task":  "DELETE /tasks/<id>",
        }
    }), 200


# ---------------------------------------------------------------------------
# Error handlers — already complete
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    """Return a JSON 404 response instead of the default HTML page."""
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Return a JSON 405 response for unsupported HTTP methods."""
    return jsonify({"error": "Method not allowed on this endpoint."}), 405


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Task Manager API starting...")
    print(f"Data file: {os.path.abspath(DATA_FILE)}")
    print("Visit http://127.0.0.1:5000 to check the health endpoint.")
    print("Press Ctrl+C to stop the server.\n")
    # debug=True reloads the server on file changes — useful during development
    app.run(debug=True)
