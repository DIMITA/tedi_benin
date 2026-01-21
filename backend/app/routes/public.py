"""
Public API routes (no authentication required)
"""
from flask import Blueprint
from flask_restx import Namespace, Resource
from sqlalchemy import func

from app import db
from app.models.geo import Commune
from app.models.agriculture import AgriStats
from app.models.realestate import RealEstateStats
from app.models.employment import EmploymentStats
from app.models.business import BusinessStats
from app.models.auth import ApiKey

# Create namespace
ns = Namespace('public', description='Public endpoints (no auth required)')

# Create blueprint for non-restx routes if needed
bp = Blueprint('public', __name__)


@ns.route('/stats')
class PublicStats(Resource):
    """Get public platform statistics"""

    @ns.doc('get_public_stats')
    def get(self):
        """Get platform statistics for landing page"""

        # Count communes
        communes_count = db.session.query(func.count(Commune.id)).scalar()

        # Count total data points across all verticals
        agri_count = db.session.query(func.count(AgriStats.id)).scalar()
        real_estate_count = db.session.query(func.count(RealEstateStats.id)).scalar()
        employment_count = db.session.query(func.count(EmploymentStats.id)).scalar()
        business_count = db.session.query(func.count(BusinessStats.id)).scalar()

        total_data_points = agri_count + real_estate_count + employment_count + business_count

        # Count active API keys (keys that are active and not expired)
        active_keys_count = db.session.query(func.count(ApiKey.id)).filter(
            ApiKey.is_active == True
        ).scalar()

        # Data sources count (fixed - FAOSTAT, World Bank, ILOSTAT, OpenStreetMap)
        data_sources_count = 4

        return {
            'communes': communes_count,
            'data_sources': data_sources_count,
            'data_points': total_data_points,
            'active_users': active_keys_count,
            'breakdown': {
                'agriculture': agri_count,
                'real_estate': real_estate_count,
                'employment': employment_count,
                'business': business_count
            }
        }

@ns.route('/communes')
class PublicCommunes(Resource):
    """Get public list of communes for map display"""

    @ns.doc('get_public_communes')
    def get(self):
        """Get list of communes with coordinates for landing page map"""
        communes = db.session.query(Commune).all()
        
        return {
            'data': [
                {
                    'id': c.id,
                    'name': c.name,
                    'center_lat': c.center_lat,
                    'center_lon': c.center_lon,
                    'population': c.population,
                    'area_km2': c.area_km2,
                    'region': {
                        'id': c.region.id if c.region else None,
                        'name': c.region.name if c.region else None
                    } if c.region else None
                }
                for c in communes
            ]
        }


@ns.route('/communes/<int:commune_id>/summary')
class PublicCommuneSummary(Resource):
    """Get summary statistics for a commune (public)"""

    @ns.doc('get_commune_summary')
    def get(self, commune_id):
        """Get basic statistics summary for a commune - for landing page"""
        commune = db.session.query(Commune).get(commune_id)
        if not commune:
            return {'error': 'Commune not found'}, 404

        # Count records per sector for this commune
        agri_count = db.session.query(func.count(AgriStats.id)).filter(
            AgriStats.commune_id == commune_id
        ).scalar()
        
        real_estate_count = db.session.query(func.count(RealEstateStats.id)).filter(
            RealEstateStats.commune_id == commune_id
        ).scalar()
        
        employment_count = db.session.query(func.count(EmploymentStats.id)).filter(
            EmploymentStats.commune_id == commune_id
        ).scalar()
        
        business_count = db.session.query(func.count(BusinessStats.id)).filter(
            BusinessStats.commune_id == commune_id
        ).scalar()

        # Get top crops for this commune
        top_crops_query = db.session.query(
            AgriStats.crop_id,
            func.count(AgriStats.id).label('count')
        ).filter(
            AgriStats.commune_id == commune_id
        ).group_by(AgriStats.crop_id).order_by(func.count(AgriStats.id).desc()).limit(3).all()

        top_crops = []
        for crop_id, count in top_crops_query:
            from app.models.agriculture import Crop
            crop = db.session.query(Crop).get(crop_id)
            if crop:
                top_crops.append(crop.name)

        return {
            'commune': {
                'id': commune.id,
                'name': commune.name,
                'population': commune.population,
                'area_km2': commune.area_km2
            },
            'statistics': {
                'agriculture': agri_count,
                'real_estate': real_estate_count,
                'employment': employment_count,
                'business': business_count,
                'total': agri_count + real_estate_count + employment_count + business_count
            },
            'top_crops': top_crops
        }