"""
Base model for all database models
"""
from datetime import datetime
from app import db


class BaseModel(db.Model):
    """
    Base model class with common fields
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, exclude=None):
        """
        Convert model instance to dictionary

        Args:
            exclude: List of fields to exclude

        Returns:
            Dictionary representation of the model
        """
        exclude = exclude or []
        data = {}

        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                # Handle datetime objects
                if isinstance(value, datetime):
                    data[column.name] = value.isoformat()
                else:
                    data[column.name] = value

        return data

    def save(self):
        """Save instance to database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete instance from database"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        """Get instance by ID"""
        return cls.query.get(id)

    @classmethod
    def get_all(cls, limit=None, offset=None):
        """Get all instances with optional pagination"""
        query = cls.query
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()
