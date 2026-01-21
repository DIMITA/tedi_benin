"""
Authentication and API key management routes
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from datetime import datetime
import os

from app import db
from app.models.auth import ApiKey

# Admin secret key (should be in environment variable)
ADMIN_SECRET = os.environ.get('TEDI_ADMIN_SECRET', 'tedi-admin-secret-2026')

# Create namespace
ns = Namespace('auth', description='Authentication and API key management')

# Define models for documentation
api_key_create_model = ns.model('ApiKeyCreate', {
    'name': fields.String(required=True, description='Friendly name for the key'),
    'owner_name': fields.String(required=True, description='Name of the key owner'),
    'owner_email': fields.String(required=True, description='Email of the key owner'),
    'owner_organization': fields.String(required=False, description='Organization of the owner'),
    'expires_in_days': fields.Integer(required=False, default=365, description='Days until expiration'),
    'scopes': fields.List(fields.String, required=False, description='Permission scopes'),
})

register_model = ns.model('Register', {
    'name': fields.String(required=True, description='Your full name'),
    'email': fields.String(required=True, description='Your email address'),
    'organization': fields.String(required=False, description='Your organization'),
})

api_key_response_model = ns.model('ApiKeyResponse', {
    'id': fields.Integer(required=True, description='API Key ID'),
    'key': fields.String(required=True, description='The actual API key'),
    'name': fields.String(required=True, description='Friendly name'),
    'owner_name': fields.String(required=True, description='Owner name'),
    'owner_email': fields.String(required=True, description='Owner email'),
    'owner_organization': fields.String(description='Organization'),
    'is_active': fields.Boolean(description='Is the key active'),
    'is_admin': fields.Boolean(description='Is admin key'),
    'can_export': fields.Boolean(description='Can export data'),
    'can_api_direct': fields.Boolean(description='Can call API directly'),
    'expires_at': fields.DateTime(description='Expiration date'),
    'created_at': fields.DateTime(description='Creation date'),
    'last_used_at': fields.DateTime(description='Last usage date'),
    'total_requests': fields.Integer(description='Total requests made'),
    'scopes': fields.List(fields.String, description='Permission scopes'),
})


@ns.route('/keys')
class ApiKeyList(Resource):
    """API Key list operations"""

    @ns.doc('list_api_keys')
    @ns.param('email', 'Filter by owner email', required=False)
    def get(self):
        """List API keys (for admin)"""
        # In a real app, this should require admin authentication
        email = request.args.get('email')

        query = ApiKey.query
        if email:
            query = query.filter_by(owner_email=email)

        keys = query.all()
        return {
            'data': [k.to_dict(include_key=False) for k in keys],
            'total': len(keys)
        }, 200

    @ns.doc('create_api_key')
    @ns.expect(api_key_create_model)
    @ns.marshal_with(api_key_response_model, code=201)
    def post(self):
        """Create a new API key"""
        data = request.json

        # Validate required fields
        required_fields = ['name', 'owner_name', 'owner_email']
        for field in required_fields:
            if field not in data:
                ns.abort(400, f'Missing required field: {field}')

        # Create API key
        try:
            api_key = ApiKey.create_key(
                name=data['name'],
                owner_name=data['owner_name'],
                owner_email=data['owner_email'],
                owner_organization=data.get('owner_organization'),
                expires_in_days=data.get('expires_in_days', 365),
                scopes=data.get('scopes', ['agriculture:read'])
            )

            db.session.add(api_key)
            db.session.commit()

            # Return with the actual key (only shown once)
            return api_key.to_dict(include_key=True), 201

        except Exception as e:
            db.session.rollback()
            ns.abort(500, f'Error creating API key: {str(e)}')


@ns.route('/keys/<int:key_id>')
@ns.param('key_id', 'API Key identifier')
class ApiKeyDetail(Resource):
    """API Key detail operations"""

    @ns.doc('get_api_key')
    def get(self, key_id):
        """Get API key details (without the actual key)"""
        api_key = ApiKey.get_by_id(key_id)
        if not api_key:
            ns.abort(404, f'API Key {key_id} not found')

        return {
            'data': api_key.to_dict(include_key=False)
        }, 200

    @ns.doc('update_api_key')
    def patch(self, key_id):
        """Update API key (activate/deactivate)"""
        api_key = ApiKey.get_by_id(key_id)
        if not api_key:
            ns.abort(404, f'API Key {key_id} not found')

        data = request.json

        # Update allowed fields
        if 'is_active' in data:
            api_key.is_active = data['is_active']
        if 'scopes' in data:
            api_key.scopes = data['scopes']

        try:
            db.session.commit()
            return {
                'data': api_key.to_dict(include_key=False),
                'message': 'API key updated successfully'
            }, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f'Error updating API key: {str(e)}')

    @ns.doc('delete_api_key')
    def delete(self, key_id):
        """Delete API key"""
        api_key = ApiKey.get_by_id(key_id)
        if not api_key:
            ns.abort(404, f'API Key {key_id} not found')

        try:
            db.session.delete(api_key)
            db.session.commit()
            return {'message': f'API key {key_id} deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f'Error deleting API key: {str(e)}')


@ns.route('/validate')
class ApiKeyValidate(Resource):
    """API Key validation endpoint"""

    @ns.doc('validate_api_key')
    @ns.param('key', 'API Key to validate', required=True, _in='query')
    def get(self):
        """Validate an API key"""
        key = request.args.get('key')

        if not key:
            ns.abort(400, 'Missing key parameter')

        api_key = ApiKey.query.filter_by(key=key).first()

        if not api_key:
            return {'valid': False, 'message': 'API key not found'}, 404

        is_valid = api_key.is_valid()

        return {
            'valid': is_valid,
            'message': 'API key is valid' if is_valid else 'API key is expired or inactive',
            'data': api_key.to_dict(include_key=False) if is_valid else None
        }, 200 if is_valid else 401


@ns.route('/register')
class Register(Resource):
    """Public registration endpoint for regular users"""

    @ns.doc('register_user')
    @ns.expect(register_model)
    def post(self):
        """
        Register and get an API key (public endpoint).
        Created keys have limited permissions:
        - Can view data on frontend
        - Cannot export data
        - Cannot call API directly (only through frontend)
        """
        data = request.json

        # Validate required fields
        if not data.get('name'):
            ns.abort(400, 'Name is required')
        if not data.get('email'):
            ns.abort(400, 'Email is required')

        # Check if email already has a key
        existing_key = ApiKey.query.filter_by(owner_email=data['email']).first()
        if existing_key:
            # If key exists and is active, return error
            if existing_key.is_valid():
                ns.abort(409, 'An API key already exists for this email. Please use your existing key or contact support.')
            else:
                # If expired/inactive, delete old one and create new
                db.session.delete(existing_key)
                db.session.commit()

        # Create API key with limited permissions
        try:
            api_key = ApiKey.create_key(
                name=f"User Key - {data['name']}",
                owner_name=data['name'],
                owner_email=data['email'],
                owner_organization=data.get('organization'),
                expires_in_days=365,
                scopes=['agriculture:read', 'realestate:read', 'employment:read', 'business:read'],
                is_admin=False,
                can_export=False,
                can_api_direct=False
            )

            db.session.add(api_key)
            db.session.commit()

            return {
                'message': 'Registration successful! Please save your API key - it will only be shown once.',
                'api_key': api_key.key,
                'data': api_key.to_dict(include_key=True)
            }, 201

        except Exception as e:
            db.session.rollback()
            ns.abort(500, f'Error during registration: {str(e)}')


def check_admin_secret():
    """Verify admin secret in request header"""
    admin_secret = request.headers.get('X-Admin-Secret')
    if not admin_secret or admin_secret != ADMIN_SECRET:
        return False
    return True


# Model for admin key creation
admin_key_create_model = ns.model('AdminKeyCreate', {
    'name': fields.String(required=True, description='Friendly name for the key'),
    'owner_name': fields.String(required=True, description='Name of the key owner'),
    'owner_email': fields.String(required=True, description='Email of the key owner'),
    'owner_organization': fields.String(required=False, description='Organization of the owner'),
    'expires_in_days': fields.Integer(required=False, default=365, description='Days until expiration'),
    'is_admin': fields.Boolean(required=False, default=False, description='Grant admin privileges'),
    'can_export': fields.Boolean(required=False, default=True, description='Allow data export'),
    'can_api_direct': fields.Boolean(required=False, default=True, description='Allow direct API access'),
    'scopes': fields.List(fields.String, required=False, description='Permission scopes'),
})


@ns.route('/admin/keys')
class AdminKeyManagement(Resource):
    """Admin-only API key management"""

    @ns.doc('admin_list_keys')
    @ns.param('X-Admin-Secret', 'Admin secret key', _in='header', required=True)
    def get(self):
        """List all API keys (admin only)"""
        if not check_admin_secret():
            ns.abort(401, 'Invalid or missing admin secret')

        keys = ApiKey.query.all()
        return {
            'data': [k.to_dict(include_key=False) for k in keys],
            'total': len(keys),
            'stats': {
                'total_keys': len(keys),
                'active_keys': len([k for k in keys if k.is_active]),
                'admin_keys': len([k for k in keys if k.is_admin]),
                'export_enabled': len([k for k in keys if k.can_export]),
                'api_direct_enabled': len([k for k in keys if k.can_api_direct])
            }
        }, 200

    @ns.doc('admin_create_key')
    @ns.expect(admin_key_create_model)
    @ns.param('X-Admin-Secret', 'Admin secret key', _in='header', required=True)
    def post(self):
        """
        Create an API key with custom permissions (admin only).
        Use this to create keys with export and direct API access.
        """
        if not check_admin_secret():
            ns.abort(401, 'Invalid or missing admin secret')

        data = request.json

        # Validate required fields
        required_fields = ['name', 'owner_name', 'owner_email']
        for field in required_fields:
            if field not in data:
                ns.abort(400, f'Missing required field: {field}')

        # Create API key with specified permissions
        try:
            api_key = ApiKey.create_key(
                name=data['name'],
                owner_name=data['owner_name'],
                owner_email=data['owner_email'],
                owner_organization=data.get('owner_organization'),
                expires_in_days=data.get('expires_in_days', 365),
                scopes=data.get('scopes', ['data:read', 'data:export', 'api:direct']),
                is_admin=data.get('is_admin', False),
                can_export=data.get('can_export', True),
                can_api_direct=data.get('can_api_direct', True)
            )

            db.session.add(api_key)
            db.session.commit()

            return {
                'message': 'API key created successfully with custom permissions.',
                'data': api_key.to_dict(include_key=True)
            }, 201

        except Exception as e:
            db.session.rollback()
            ns.abort(500, f'Error creating API key: {str(e)}')


@ns.route('/admin/keys/<int:key_id>')
@ns.param('key_id', 'API Key identifier')
class AdminKeyDetail(Resource):
    """Admin-only API key detail operations"""

    @ns.doc('admin_update_key')
    @ns.param('X-Admin-Secret', 'Admin secret key', _in='header', required=True)
    def patch(self, key_id):
        """Update API key permissions (admin only)"""
        if not check_admin_secret():
            ns.abort(401, 'Invalid or missing admin secret')

        api_key = ApiKey.get_by_id(key_id)
        if not api_key:
            ns.abort(404, f'API Key {key_id} not found')

        data = request.json

        # Update allowed fields
        if 'is_active' in data:
            api_key.is_active = data['is_active']
        if 'is_admin' in data:
            api_key.is_admin = data['is_admin']
        if 'can_export' in data:
            api_key.can_export = data['can_export']
        if 'can_api_direct' in data:
            api_key.can_api_direct = data['can_api_direct']
        if 'scopes' in data:
            api_key.scopes = data['scopes']

        try:
            db.session.commit()
            return {
                'data': api_key.to_dict(include_key=False),
                'message': 'API key updated successfully'
            }, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f'Error updating API key: {str(e)}')

    @ns.doc('admin_delete_key')
    @ns.param('X-Admin-Secret', 'Admin secret key', _in='header', required=True)
    def delete(self, key_id):
        """Delete API key (admin only)"""
        if not check_admin_secret():
            ns.abort(401, 'Invalid or missing admin secret')

        api_key = ApiKey.get_by_id(key_id)
        if not api_key:
            ns.abort(404, f'API Key {key_id} not found')

        try:
            db.session.delete(api_key)
            db.session.commit()
            return {'message': f'API key {key_id} deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            ns.abort(500, f'Error deleting API key: {str(e)}')
