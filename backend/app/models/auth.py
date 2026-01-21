"""
Authentication and authorization models
"""
import secrets
from datetime import datetime, timedelta
from app import db
from app.models.base import BaseModel


class ApiKey(BaseModel):
    """API Key model for authentication"""
    __tablename__ = 'api_keys'

    # Key info
    key = db.Column(db.String(64), nullable=False, unique=True, index=True)
    name = db.Column(db.String(100), nullable=False)  # Friendly name for the key
    description = db.Column(db.Text, nullable=True)

    # Owner info
    owner_name = db.Column(db.String(200), nullable=False)
    owner_email = db.Column(db.String(200), nullable=False, index=True)
    owner_organization = db.Column(db.String(200), nullable=True)

    # Access control
    is_active = db.Column(db.Boolean, default=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Permission levels
    is_admin = db.Column(db.Boolean, default=False, index=True)  # Admin users
    can_export = db.Column(db.Boolean, default=False)  # Can export data (CSV)
    can_api_direct = db.Column(db.Boolean, default=False)  # Can call API directly (not from frontend)

    # Rate limiting
    rate_limit_per_hour = db.Column(db.Integer, default=1000)
    rate_limit_per_day = db.Column(db.Integer, default=10000)

    # Usage tracking
    last_used_at = db.Column(db.DateTime, nullable=True)
    total_requests = db.Column(db.Integer, default=0)

    # Scopes/permissions (JSON array of strings)
    scopes = db.Column(db.JSON, default=list)  # e.g., ["agriculture:read", "real-estate:read"]

    def __repr__(self):
        return f'<ApiKey {self.name} ({self.owner_email})>'

    @staticmethod
    def generate_key():
        """Generate a secure API key"""
        return secrets.token_urlsafe(48)  # 64 characters when base64 encoded

    @classmethod
    def create_key(cls, name, owner_name, owner_email, owner_organization=None, 
                   expires_in_days=365, scopes=None, is_admin=False, can_export=False, can_api_direct=False):
        """
        Create a new API key

        Args:
            name: Friendly name for the key
            owner_name: Name of the key owner
            owner_email: Email of the key owner
            owner_organization: Organization of the owner
            expires_in_days: Number of days until expiration (None for no expiration)
            scopes: List of permission scopes
            is_admin: Whether this is an admin key
            can_export: Whether this key can export data
            can_api_direct: Whether this key can call API directly

        Returns:
            ApiKey instance
        """
        key = cls.generate_key()
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        api_key = cls(
            key=key,
            name=name,
            owner_name=owner_name,
            owner_email=owner_email,
            owner_organization=owner_organization,
            expires_at=expires_at,
            scopes=scopes or [],
            is_admin=is_admin,
            can_export=can_export,
            can_api_direct=can_api_direct
        )

        return api_key

    def is_valid(self):
        """Check if the API key is valid"""
        if not self.is_active:
            return False

        if self.expires_at and self.expires_at < datetime.utcnow():
            return False

        return True

    def has_scope(self, required_scope):
        """
        Check if the key has a specific scope

        Args:
            required_scope: Scope string (e.g., "agriculture:read")

        Returns:
            Boolean
        """
        if not self.scopes:
            return False

        # Check exact match or wildcard
        for scope in self.scopes:
            if scope == required_scope or scope == '*':
                return True

            # Check prefix match (e.g., "agriculture:*" matches "agriculture:read")
            if scope.endswith(':*') and required_scope.startswith(scope[:-1]):
                return True

        return False

    def record_usage(self):
        """Record API key usage"""
        self.last_used_at = datetime.utcnow()
        self.total_requests += 1
        db.session.commit()

    def to_dict(self, include_key=False, exclude=None):
        """
        Convert to dictionary

        Args:
            include_key: Include the actual API key (default: False for security)
            exclude: Fields to exclude

        Returns:
            Dictionary representation
        """
        exclude = exclude or []
        if not include_key:
            exclude.append('key')

        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data['is_valid'] = self.is_valid()
        data['is_expired'] = self.expires_at and self.expires_at < datetime.utcnow() if self.expires_at else False

        return data
