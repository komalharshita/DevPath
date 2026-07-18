"""Routes for certificate generation and verification.

Provides endpoints for generating PDF certificates when users complete
learning paths, and verifying certificate authenticity.
"""

from flask import Blueprint, jsonify, render_template_string, request
from datetime import datetime
import json

certificate_bp = Blueprint('certificates', __name__, url_prefix='/certificates')


@certificate_bp.route('/generate', methods=['POST'])
def generate_certificate():
    """Generate and store a completion certificate.

    Endpoint: POST /certificates/generate
    Expected JSON: {
        "user_id": int,
        "path_id": int,
        "user_name": str,
        "path_name": str
    }

    Returns:
        JSON response with certificate details and verification code
    """
    try:
        data = request.json

        # Validate required fields
        required_fields = ['user_id', 'path_id', 'user_name', 'path_name']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        # Get database from app context
        from app import get_db
        db = get_db()

        # Import certificate generator
        from utils.certificate_generator import CertificateGenerator
        cert_gen = CertificateGenerator(db)

        # Create certificate metadata
        cert_data = cert_gen.create_certificate_metadata(
            data['user_name'],
            data['path_name'],
            data['path_id']
        )

        # Store certificate record in database
        success = cert_gen.store_certificate_record(
            data['user_id'],
            data['path_id'],
            cert_data['verification_code']
        )

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to store certificate'
            }), 500

        return jsonify({
            'success': True,
            'certificate': {
                'verification_code': cert_data['verification_code'],
                'completion_date': cert_data['completion_date'],
                'learner_name': cert_data['learner_name'],
                'path_name': cert_data['path_name'],
                'path_id': cert_data['path_id']
            }
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@certificate_bp.route('/verify/<verification_code>', methods=['GET'])
def verify_certificate(verification_code):
    """Verify a certificate using its verification code.

    This endpoint is public and allows anyone to verify certificate authenticity.

    Endpoint: GET /certificates/verify/<verification_code>

    Returns:
        JSON response with certificate verification status
    """
    try:
        # Get database from app context
        from app import get_db
        db = get_db()

        # Import certificate generator
        from utils.certificate_generator import CertificateGenerator
        cert_gen = CertificateGenerator(db)

        # Verify certificate
        cert_data = cert_gen.verify_certificate(verification_code)

        if cert_data:
            return jsonify({
                'valid': True,
                'certificate': cert_data
            }), 200
        else:
            return jsonify({
                'valid': False,
                'message': 'Certificate not found or invalid'
            }), 404

    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500


@certificate_bp.route('/download/<int:path_id>', methods=['POST'])
def download_certificate(path_id):
    """Download certificate PDF for a completed path.

    Endpoint: POST /certificates/download/<path_id>
    Expected JSON: { "user_id": int }

    Returns:
        JSON with certificate download data for client-side PDF generation
    """
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id required'
            }), 400

        # Get database from app context
        from app import get_db
        db = get_db()

        # Import certificate generator
        from utils.certificate_generator import CertificateGenerator
        cert_gen = CertificateGenerator(db)

        # Get existing certificate
        cert_data = cert_gen.get_certificate_by_path(user_id, path_id)

        if not cert_data:
            return jsonify({
                'success': False,
                'error': 'Certificate not found. Complete the path first.'
            }), 404

        # Get path and user details from database
        cursor = db.execute(
            'SELECT name FROM paths WHERE id = ?', (path_id,)
        )
        path = cursor.fetchone()

        cursor = db.execute(
            'SELECT name FROM users WHERE id = ?', (user_id,)
        )
        user = cursor.fetchone()

        if not path or not user:
            return jsonify({
                'success': False,
                'error': 'Path or user not found'
            }), 404

        return jsonify({
            'success': True,
            'certificate': {
                'learner_name': user[0],
                'path_name': path[0],
                'path_id': path_id,
                'completion_date': cert_data['completion_date'],
                'verification_code': cert_data['verification_code']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
