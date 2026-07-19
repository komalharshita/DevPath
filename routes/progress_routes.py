"""Routes for progress tracking and dashboard.

Provides endpoints for tracking learner progress and retrieving
dashboard metrics including streaks, charts, and path completion.
"""

from flask import Blueprint, jsonify, request

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')


@progress_bp.route('/user/<int:user_id>/dashboard', methods=['GET'])
def get_progress_dashboard(user_id):
    """Get progress dashboard data for user.

    Endpoint: GET /progress/user/<user_id>/dashboard

    Returns:
        JSON with completion %, streaks, weekly activity, path progress
    """
    try:
        from utils.progress_tracker import ProgressTracker
        from app import get_db

        db = get_db()
        tracker = ProgressTracker(db)

        progress = tracker.get_user_progress(user_id)

        return jsonify({
            'success': True,
            'progress': progress
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@progress_bp.route('/topic/<int:topic_id>/complete', methods=['POST'])
def mark_topic_complete(topic_id):
    """Mark a topic as completed.

    Endpoint: POST /progress/topic/<topic_id>/complete
    Expected JSON: { "user_id": int }

    Returns:
        JSON success/error response
    """
    try:
        data = request.json

        if 'user_id' not in data:
            return jsonify({
                'success': False,
                'error': 'user_id required'
            }), 400

        from utils.progress_tracker import ProgressTracker
        from app import get_db

        db = get_db()
        tracker = ProgressTracker(db)

        success = tracker.mark_topic_complete(data['user_id'], topic_id)

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update progress'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Topic marked as complete'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@progress_bp.route('/activity/record', methods=['POST'])
def record_activity():
    """Record user activity on a topic.

    Endpoint: POST /progress/activity/record
    Expected JSON: {
        "user_id": int,
        "topic_id": int
    }

    Returns:
        JSON success/error response
    """
    try:
        data = request.json

        required = ['user_id', 'topic_id']
        if not all(f in data for f in required):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        from utils.progress_tracker import ProgressTracker
        from app import get_db

        db = get_db()
        tracker = ProgressTracker(db)

        success = tracker.record_activity(data['user_id'], data['topic_id'])

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to record activity'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Activity recorded'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
