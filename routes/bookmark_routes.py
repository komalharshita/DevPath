"""Routes for bookmark management.

Provides endpoints for adding, removing, and retrieving bookmarks for
resources and learning paths.
"""

from flask import Blueprint, jsonify, request

bookmark_bp = Blueprint('bookmarks', __name__, url_prefix='/bookmarks')


@bookmark_bp.route('/add', methods=['POST'])
def add_bookmark():
    """Add a bookmark for authenticated user.

    Endpoint: POST /bookmarks/add
    Expected JSON: {
        "user_id": int,
        "resource_type": str,
        "resource_id": int,
        "resource_name": str
    }

    Returns:
        JSON success/error response
    """
    try:
        data = request.json

        required = ['user_id', 'resource_type', 'resource_id', 'resource_name']
        if not all(f in data for f in required):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        from utils.bookmark_manager import BookmarkManager
        from app import get_db

        db = get_db()
        manager = BookmarkManager(db)

        bookmark_id = manager.add_bookmark(
            data['user_id'],
            data['resource_type'],
            data['resource_id'],
            data['resource_name']
        )

        if not bookmark_id:
            return jsonify({
                'success': False,
                'error': 'Failed to add bookmark'
            }), 500

        return jsonify({
            'success': True,
            'bookmark_id': bookmark_id,
            'message': 'Bookmark added'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bookmark_bp.route('/remove', methods=['POST'])
def remove_bookmark():
    """Remove a bookmark.

    Endpoint: POST /bookmarks/remove
    Expected JSON: {
        "user_id": int,
        "resource_type": str,
        "resource_id": int
    }

    Returns:
        JSON success/error response
    """
    try:
        data = request.json

        required = ['user_id', 'resource_type', 'resource_id']
        if not all(f in data for f in required):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        from utils.bookmark_manager import BookmarkManager
        from app import get_db

        db = get_db()
        manager = BookmarkManager(db)

        success = manager.remove_bookmark(
            data['user_id'],
            data['resource_type'],
            data['resource_id']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Bookmark not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Bookmark removed'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bookmark_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_bookmarks(user_id):
    """Get all bookmarks for a user.

    Endpoint: GET /bookmarks/user/<user_id>
    Query params: resource_type=str (optional filter)

    Returns:
        JSON array of bookmarks
    """
    try:
        resource_type = request.args.get('resource_type')

        from utils.bookmark_manager import BookmarkManager
        from app import get_db

        db = get_db()
        manager = BookmarkManager(db)

        bookmarks = manager.get_user_bookmarks(user_id, resource_type)

        return jsonify({
            'success': True,
            'bookmarks': bookmarks,
            'count': len(bookmarks)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bookmark_bp.route('/check', methods=['POST'])
def check_bookmark():
    """Check if resource is bookmarked.

    Endpoint: POST /bookmarks/check
    Expected JSON: {
        "user_id": int,
        "resource_type": str,
        "resource_id": int
    }

    Returns:
        JSON with bookmark status
    """
    try:
        data = request.json

        from utils.bookmark_manager import BookmarkManager
        from app import get_db

        db = get_db()
        manager = BookmarkManager(db)

        is_bookmarked = manager.is_bookmarked(
            data.get('user_id'),
            data.get('resource_type'),
            data.get('resource_id')
        )

        return jsonify({
            'success': True,
            'bookmarked': is_bookmarked
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bookmark_bp.route('/popular/<resource_type>', methods=['GET'])
def get_popular_bookmarks(resource_type):
    """Get most bookmarked resources of a type.

    Endpoint: GET /bookmarks/popular/<resource_type>
    Query params: limit=10 (optional)

    Returns:
        JSON array of popular bookmarked resources
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 100)

        from utils.bookmark_manager import BookmarkManager
        from app import get_db

        db = get_db()
        manager = BookmarkManager(db)

        popular = manager.get_popular_bookmarks(resource_type, limit)

        return jsonify({
            'success': True,
            'popular': popular
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
