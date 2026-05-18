# routes/main_routes.py
# All application routes registered as a Flask Blueprint.
# Each route is kept thin: it validates input, calls a utility function,
# and returns a response. No business logic lives here.

from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort
import time
from utils.recommender import get_recommendations, validate_recommendation_inputs
from utils.data_loader import find_project_by_id, get_project_stats
from utils.file_server import read_starter_code, resolve_starter_file, get_starter_code_dir

from utils.embedding_helpers import get_embedding, calculate_cosine_similarity

from utils.redis_client import get_redis_client
from utils.kafka_producer import get_kafka_producer

PROJECTS_JSON_PATH = "data/projects.json"
EMBEDDINGS_PKL_PATH = "data/project_embeddings.pkl"

# Create the Blueprint that app.py will register
main = Blueprint("main", __name__)


@main.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({'error': 'Missing userId parameter'}), 400

    try:
        r = get_redis_client()
        redis_key = f"user:history:{user_id}"

        # Pull top 20 interactive IDs by descending score sorting logic
        raw_history = r.zrevrange(redis_key, 0, 19)

        response = jsonify({'success': True, 'suggestions': raw_history})
        if hasattr(request, 'rate_limit_headers'):
            response.headers.update(request.rate_limit_headers)
        return response

    except Exception as e:
        return jsonify({'error': 'Internal Caching Failure', 'details': str(e)}), 500



@main.route('/api/discover', methods=['POST'])
def discover_projects():
    """
    Accepts natural language descriptions of user interests and matches them 
    against pre-calculated project embeddings using Cosine Similarity metrics.
    """
    data = request.get_json() or {}
    user_query = data.get("query", "").strip()
    
    if not user_query:
        return jsonify({"error": "Query string is required"}), 400

    # Fallback to direct text search if the pre-computed embedding asset file is missing
    if not os.path.exists(EMBEDDINGS_PKL_PATH):
        return jsonify({"error": "Embedding index matrix is missing. Run generation script first."}), 500

    try:
        # 1. Vectorize the live user input context string on the fly
        user_vector = get_embedding(user_query)
        
        # 2. Load the static project vector collection maps
        with open(EMBEDDINGS_PKL_PATH, "rb") as f:
            project_embeddings = pickle.load(f)
            
        # 3. Compute semantic match rankings across the dataset matrix
        scored_matches = []
        for item in project_embeddings:
            score = calculate_cosine_similarity(user_vector, item["vector"])
            scored_matches.append({
                "id": item["id"],
                "title": item["title"],
                "similarity_score": round(score, 4)
            })
            
        # Sort collections by highest similarity matching coefficients down
        scored_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # 4. Map the top 3 highest vector scoring indices back to the full project schemas
        top_3_matches = scored_matches[:3]
        
        with open(PROJECTS_JSON_PATH, "r") as f:
            all_projects = json.load(f)
            
        project_lookup_map = {p["id"]: p for p in all_projects}
        
        enriched_recommendations = []
        for match in top_3_matches:
            project_details = project_lookup_map.get(match["id"])
            if project_details:
                # Append the calculation matching metrics to the output payload
                result_item = project_details.copy()
                result_item["match_score"] = match["similarity_score"]
                enriched_recommendations.append(result_item)

        return jsonify({
            "success": True,
            "results": enriched_recommendations
        })

    except Exception as e:
        return jsonify({
            "error": "Semantic matching pipeline failed processing execution instance",
            "details": str(e)
        }), 500


@main.route('/api/suggestions', methods=['POST'])
def log_interaction():
    data = request.get_json() or {}
    user_id = data.get('userId')
    project_id = data.get('projectId')
    interaction_type = data.get('interactionType', 'view')

    if not user_id or not project_id:
        return jsonify({'error': 'Missing required payload'}), 400

    try:
        producer = get_kafka_producer()
        payload = {
            'userId': user_id,
            'projectId': project_id,
            'interactionType': interaction_type,
            'timestamp': int(time.time() * 1000)
        }

        # Unblocking asynchronous push operation offloaded to broker topology
        producer.send('user-activity', key=user_id, value=payload)

        response = jsonify({'success': True, 'message': 'Interaction logged.'})
        if hasattr(request, 'rate_limit_headers'):
            response.headers.update(request.rate_limit_headers)
        return response

    except Exception as e:
        return jsonify({'error': 'Kafka Event Logging Pipeline Failure', 'details': str(e)}), 500

@main.route("/")
def index():
    """Render the homepage with the skill input form and dynamic stats."""
    stats = get_project_stats()
    return render_template("index.html", stats=stats)


@main.route("/api/recommend", methods=["POST"])
def recommend():
    """
    Accept a JSON body with user inputs and return matching project recommendations.

    Expected JSON fields:
        skills   (str) - comma-separated list of skills
        level    (str) - Beginner | Intermediate | Advanced
        interest (str) - Web | Data | Education | Automation | Games
        time     (str) - Low | Medium | High
    """
    payload = request.get_json()

    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    skills            = payload.get("skills", "").strip()
    level             = payload.get("level", "").strip()
    interest          = payload.get("interest", "").strip()
    time_availability = payload.get("time", "").strip()

    # Validate before running the recommendation engine
    errors = validate_recommendation_inputs(skills, level, interest, time_availability)
    if errors:
        # Return only the first error to keep the UI message clean
        return jsonify({"error": errors[0]}), 400

    results = get_recommendations(skills, level, interest, time_availability)

    if not results:
        return jsonify({
            "projects": [],
            "message": (
                "No projects matched your inputs. "
                "Try different skills or broaden your interest area."
            )
        }), 200

    return jsonify({"projects": results}), 200


@main.route("/project/<int:project_id>")
def project_detail(project_id):
    """Render the full detail page for a single project."""
    project = find_project_by_id(project_id)
    if not project:
        abort(404)
    return render_template("project.html", project=project)


@main.route("/project/<int:project_id>/code")
def view_code(project_id):
    """Return the starter code file contents as JSON for inline display."""
    project = find_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404

    code_data = read_starter_code(project)
    if not code_data:
        return jsonify({"error": "Starter code not available for this project."}), 404

    return jsonify(code_data), 200


@main.route("/project/<int:project_id>/download")
def download_code(project_id):
    """Serve the starter code file as a downloadable attachment."""
    project = find_project_by_id(project_id)
    if not project:
        abort(404)

    full_path = resolve_starter_file(project)
    if not full_path:
        abort(404)

    import os
    filename = os.path.basename(full_path)
    return send_from_directory(get_starter_code_dir(), filename, as_attachment=True)
