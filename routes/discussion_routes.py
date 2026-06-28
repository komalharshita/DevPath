"""Routes for community discussion threads on learning paths.

Provides endpoints for creating, reading, and managing discussion threads
where learners can ask questions and share knowledge about paths.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime

discussion_bp = Blueprint('discussions', __name__, url_prefix='/discussions')


@discussion_bp.route('/paths/<int:path_id>/threads', methods=['GET'])
def get_path_threads(path_id):
    """Get all discussion threads for a learning path.

    Endpoint: GET /discussions/paths/<path_id>/threads
    Query params: limit=20, offset=0, search=query

    Returns:
        JSON array of discussion thread summaries
    """
    try:
        from utils.discussion_manager import DiscussionManager
        from app import get_db

        db = get_db()
        manager = DiscussionManager(db)

        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        search = request.args.get('search', '').strip()

        if search:
            threads = manager.search_threads(path_id, search)
        else:
            threads = manager.get_path_threads(path_id, limit, offset)

        return jsonify({
            'success': True,
            'threads': threads,
            'count': len(threads)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@discussion_bp.route('/threads/<int:thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get a single discussion thread with all comments.

    Endpoint: GET /discussions/threads/<thread_id>

    Returns:
        JSON object with thread details and comments
    """
    try:
        from utils.discussion_manager import DiscussionManager
        from app import get_db

        db = get_db()
        manager = DiscussionManager(db)

        thread = manager.get_thread(thread_id)

        if not thread:
            return jsonify({
                'success': False,
                'error': 'Thread not found'
            }), 404

        return jsonify({
            'success': True,
            'thread': thread
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@discussion_bp.route('/threads', methods=['POST'])
def create_thread():
    """Create a new discussion thread.

    Endpoint: POST /discussions/threads
    Expected JSON: {
        "path_id": int,
        "user_id": int,
        "title": str,
        "body": str
    }

    Returns:
        JSON with created thread details
    """
    try:
        data = request.json

        # Validate required fields
        required = ['path_id', 'user_id', 'title', 'body']
        if not all(f in data for f in required):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        # Validate title and body length
        if len(data['title']) < 5 or len(data['title']) > 200:
            return jsonify({
                'success': False,
                'error': 'Title must be 5-200 characters'
            }), 400

        if len(data['body']) < 10:
            return jsonify({
                'success': False,
                'error': 'Body must be at least 10 characters'
            }), 400

        from utils.discussion_manager import DiscussionManager
        from app import get_db

        db = get_db()
        manager = DiscussionManager(db)

        thread_id = manager.create_thread(
            data['path_id'],
            data['user_id'],
            data['title'],
            data['body']
        )

        if not thread_id:
            return jsonify({
                'success': False,
                'error': 'Failed to create thread'
            }), 500

        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'message': 'Thread created successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@discussion_bp.route('/threads/<int:thread_id>/comments', methods=['POST'])
def add_comment(thread_id):
    """Add a comment to a discussion thread.

    Endpoint: POST /discussions/threads/<thread_id>/comments
    Expected JSON: {
        "user_id": int,
        "body": str
    }

    Returns:
        JSON with created comment details
    """
    try:
        data = request.json

        if 'user_id' not in data or 'body' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        if len(data['body']) < 3:
            return jsonify({
                'success': False,
                'error': 'Comment must be at least 3 characters'
            }), 400

        from utils.discussion_manager import DiscussionManager
        from app import get_db

        db = get_db()
        manager = DiscussionManager(db)

        comment_id = manager.add_comment(
            thread_id,
            data['user_id'],
            data['body']
        )

        if not comment_id:
            return jsonify({
                'success': False,
                'error': 'Failed to add comment'
            }), 500

        return jsonify({
            'success': True,
            'comment_id': comment_id,
            'message': 'Comment added successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@discussion_bp.route('/threads/<int:thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """Delete a discussion thread.

    Endpoint: DELETE /discussions/threads/<thread_id>
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

        from utils.discussion_manager import DiscussionManager
        from app import get_db

        db = get_db()
        manager = DiscussionManager(db)

        success = manager.delete_thread(thread_id, data['user_id'])

        if not success:
            return jsonify({
                'success': False,
                'error': 'Thread not found or unauthorized'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Thread deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
