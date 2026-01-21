"""
Export routes - Multi-format data export endpoints
"""
from flask import request, Response, g
from flask_restx import Namespace, Resource, fields

from app import db
from app.models.auth import ApiKey
from app.models.agriculture import AgriStats, Crop
from app.models.geo import Commune
from app.models.realestate import RealEstateStats, PropertyType
from app.models.employment import EmploymentStats, JobCategory
from app.models.business import BusinessStats, BusinessSector
from app.services.export import ExportService
from app.utils.auth import require_api_key

# Create namespace
ns = Namespace('export', description='Data export in multiple formats')

# Column definitions for each sector
AGRICULTURE_COLUMNS = [
    {'key': 'commune', 'label': 'Commune'},
    {'key': 'crop', 'label': 'Crop'},
    {'key': 'year', 'label': 'Year'},
    {'key': 'production_tonnes', 'label': 'Production (tonnes)'},
    {'key': 'yield_tonnes_per_ha', 'label': 'Yield (t/ha)'},
    {'key': 'area_harvested_ha', 'label': 'Area (ha)'},
    {'key': 'price_per_kg', 'label': 'Price (XOF/kg)'},
    {'key': 'is_estimated', 'label': 'Estimated'},
    {'key': 'data_quality_score', 'label': 'Quality Score'},
]

REALESTATE_COLUMNS = [
    {'key': 'commune', 'label': 'Commune'},
    {'key': 'property_type', 'label': 'Property Type'},
    {'key': 'year', 'label': 'Year'},
    {'key': 'geo_zone', 'label': 'Zone'},
    {'key': 'price_per_sqm', 'label': 'Price/sqm (XOF)'},
    {'key': 'median_price', 'label': 'Median Price (XOF)'},
    {'key': 'num_transactions', 'label': 'Transactions'},
    {'key': 'price_trend', 'label': 'Trend'},
    {'key': 'infrastructure_score', 'label': 'Infrastructure'},
    {'key': 'data_quality_score', 'label': 'Quality Score'},
]

EMPLOYMENT_COLUMNS = [
    {'key': 'commune', 'label': 'Commune'},
    {'key': 'job_category', 'label': 'Category'},
    {'key': 'year', 'label': 'Year'},
    {'key': 'total_employed', 'label': 'Employed'},
    {'key': 'unemployment_rate', 'label': 'Unemployment (%)'},
    {'key': 'informal_rate', 'label': 'Informal (%)'},
    {'key': 'median_salary', 'label': 'Median Salary (XOF)'},
    {'key': 'skill_level_index', 'label': 'Skill Level'},
    {'key': 'data_quality_score', 'label': 'Quality Score'},
]

BUSINESS_COLUMNS = [
    {'key': 'commune', 'label': 'Commune'},
    {'key': 'sector', 'label': 'Sector'},
    {'key': 'year', 'label': 'Year'},
    {'key': 'num_businesses', 'label': 'Businesses'},
    {'key': 'business_density_index', 'label': 'Density'},
    {'key': 'sector_growth_score', 'label': 'Growth'},
    {'key': 'market_saturation', 'label': 'Saturation'},
    {'key': 'competition_intensity', 'label': 'Competition'},
    {'key': 'formality_rate', 'label': 'Formality (%)'},
    {'key': 'data_quality_score', 'label': 'Quality Score'},
]


def check_export_permission():
    """Check if the current API key has export permission"""
    api_key = getattr(request, 'api_key', None)
    if not api_key:
        return False
    return api_key.can_export or api_key.is_admin


def build_export_response(content: bytes, content_type: str, filename: str) -> Response:
    """Build Flask response for file download"""
    response = Response(content, content_type=content_type)
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
    return response


@ns.route('/agriculture')
class AgricultureExport(Resource):
    """Agriculture data export"""
    
    @ns.doc('export_agriculture')
    @ns.param('format', 'Export format (csv, xlsx, json, pdf, geojson)', default='csv')
    @ns.param('year', 'Filter by year', type='integer')
    @ns.param('commune_id', 'Filter by commune ID', type='integer')
    @ns.param('crop_id', 'Filter by crop ID', type='integer')
    @require_api_key('agriculture:read')
    def get(self):
        """Export agriculture data"""
        # Check export permission
        if not check_export_permission():
            return {'message': 'Export permission required. Upgrade your API key to enable exports.'}, 403
        
        format = request.args.get('format', 'csv').lower()
        
        # Build query
        query = AgriStats.query
        
        if request.args.get('year'):
            query = query.filter(AgriStats.year == int(request.args.get('year')))
        if request.args.get('commune_id'):
            query = query.filter(AgriStats.commune_id == int(request.args.get('commune_id')))
        if request.args.get('crop_id'):
            query = query.filter(AgriStats.crop_id == int(request.args.get('crop_id')))
        
        # Limit to prevent huge exports
        data = query.limit(10000).all()
        
        # Convert to dict with relations
        data_dicts = [item.to_dict(include_relations=True) for item in data]
        
        try:
            content, content_type, filename = ExportService.export(
                data_dicts, 
                AGRICULTURE_COLUMNS,
                format,
                title="TEDI Agriculture Data Export",
                sector="agriculture"
            )
            return build_export_response(content, content_type, filename)
        except ValueError as e:
            return {'message': str(e)}, 400


@ns.route('/realestate')
class RealEstateExport(Resource):
    """Real Estate data export"""
    
    @ns.doc('export_realestate')
    @ns.param('format', 'Export format (csv, xlsx, json, pdf, geojson)', default='csv')
    @ns.param('year', 'Filter by year', type='integer')
    @ns.param('property_type_id', 'Filter by property type ID', type='integer')
    @ns.param('geo_zone', 'Filter by geo zone (urban, peri_urban, rural)')
    @ns.param('price_trend', 'Filter by price trend (decreasing, stable, increasing, increasing_strong)')
    @require_api_key('realestate:read')
    def get(self):
        """Export real estate data"""
        if not check_export_permission():
            return {'message': 'Export permission required. Upgrade your API key to enable exports.'}, 403
        
        format = request.args.get('format', 'csv').lower()
        
        query = RealEstateStats.query
        
        if request.args.get('year'):
            query = query.filter(RealEstateStats.year == int(request.args.get('year')))
        if request.args.get('property_type_id'):
            query = query.filter(RealEstateStats.property_type_id == int(request.args.get('property_type_id')))
        if request.args.get('geo_zone'):
            query = query.filter(RealEstateStats.geo_zone == request.args.get('geo_zone'))
        if request.args.get('price_trend'):
            query = query.filter(RealEstateStats.price_trend == request.args.get('price_trend'))
        
        data = query.limit(10000).all()
        data_dicts = [item.to_dict(include_relations=True) for item in data]
        
        try:
            content, content_type, filename = ExportService.export(
                data_dicts,
                REALESTATE_COLUMNS,
                format,
                title="TEDI Real Estate Data Export",
                sector="realestate"
            )
            return build_export_response(content, content_type, filename)
        except ValueError as e:
            return {'message': str(e)}, 400


@ns.route('/employment')
class EmploymentExport(Resource):
    """Employment data export"""
    
    @ns.doc('export_employment')
    @ns.param('format', 'Export format (csv, xlsx, json, pdf, geojson)', default='csv')
    @ns.param('year', 'Filter by year', type='integer')
    @ns.param('job_category_id', 'Filter by job category ID', type='integer')
    @ns.param('sector', 'Filter by sector (primary, secondary, tertiary)')
    @ns.param('salary_range', 'Filter by salary range (low, medium, high, very_high)')
    @require_api_key('employment:read')
    def get(self):
        """Export employment data"""
        if not check_export_permission():
            return {'message': 'Export permission required. Upgrade your API key to enable exports.'}, 403
        
        format = request.args.get('format', 'csv').lower()
        
        query = EmploymentStats.query
        
        if request.args.get('year'):
            query = query.filter(EmploymentStats.year == int(request.args.get('year')))
        if request.args.get('job_category_id'):
            query = query.filter(EmploymentStats.job_category_id == int(request.args.get('job_category_id')))
        if request.args.get('sector'):
            query = query.join(JobCategory).filter(JobCategory.sector == request.args.get('sector'))
        if request.args.get('salary_range'):
            query = query.filter(EmploymentStats.salary_range_estimation == request.args.get('salary_range'))
        
        data = query.limit(10000).all()
        data_dicts = [item.to_dict(include_relations=True) for item in data]
        
        try:
            content, content_type, filename = ExportService.export(
                data_dicts,
                EMPLOYMENT_COLUMNS,
                format,
                title="TEDI Employment Data Export",
                sector="employment"
            )
            return build_export_response(content, content_type, filename)
        except ValueError as e:
            return {'message': str(e)}, 400


@ns.route('/business')
class BusinessExport(Resource):
    """Business data export"""
    
    @ns.doc('export_business')
    @ns.param('format', 'Export format (csv, xlsx, json, pdf, geojson)', default='csv')
    @ns.param('year', 'Filter by year', type='integer')
    @ns.param('sector_id', 'Filter by business sector ID', type='integer')
    @ns.param('market_saturation', 'Filter by market saturation level')
    @ns.param('competition', 'Filter by competition intensity (low, medium, high)')
    @require_api_key('business:read')
    def get(self):
        """Export business data"""
        if not check_export_permission():
            return {'message': 'Export permission required. Upgrade your API key to enable exports.'}, 403
        
        format = request.args.get('format', 'csv').lower()
        
        query = BusinessStats.query
        
        if request.args.get('year'):
            query = query.filter(BusinessStats.year == int(request.args.get('year')))
        if request.args.get('sector_id'):
            query = query.filter(BusinessStats.sector_id == int(request.args.get('sector_id')))
        if request.args.get('market_saturation'):
            query = query.filter(BusinessStats.market_saturation == request.args.get('market_saturation'))
        if request.args.get('competition'):
            query = query.filter(BusinessStats.competition_intensity == request.args.get('competition'))
        
        data = query.limit(10000).all()
        data_dicts = [item.to_dict(include_relations=True) for item in data]
        
        try:
            content, content_type, filename = ExportService.export(
                data_dicts,
                BUSINESS_COLUMNS,
                format,
                title="TEDI Business Data Export",
                sector="business"
            )
            return build_export_response(content, content_type, filename)
        except ValueError as e:
            return {'message': str(e)}, 400


@ns.route('/formats')
class ExportFormats(Resource):
    """List available export formats"""
    
    @ns.doc('list_formats')
    def get(self):
        """Get list of available export formats"""
        return {
            'formats': [
                {
                    'id': 'csv',
                    'name': 'CSV',
                    'description': 'Comma-separated values, compatible with Excel and most tools',
                    'extension': '.csv',
                    'mime_type': 'text/csv'
                },
                {
                    'id': 'xlsx',
                    'name': 'Excel',
                    'description': 'Microsoft Excel format with formatting',
                    'extension': '.xlsx',
                    'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                },
                {
                    'id': 'json',
                    'name': 'JSON',
                    'description': 'JavaScript Object Notation, ideal for developers',
                    'extension': '.json',
                    'mime_type': 'application/json'
                },
                {
                    'id': 'pdf',
                    'name': 'PDF',
                    'description': 'Portable Document Format, ideal for reports',
                    'extension': '.pdf',
                    'mime_type': 'application/pdf'
                },
                {
                    'id': 'geojson',
                    'name': 'GeoJSON',
                    'description': 'Geographic JSON, ideal for mapping applications',
                    'extension': '.geojson',
                    'mime_type': 'application/geo+json'
                }
            ]
        }, 200
