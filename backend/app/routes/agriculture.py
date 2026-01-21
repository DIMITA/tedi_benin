"""
Agriculture API routes
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy import and_, func, desc
from statistics import mean, stdev

from app import db
from app.models.geo import Commune, Region
from app.models.agriculture import Crop, AgriStats
from app.utils.auth import require_api_key

# Create namespace
ns = Namespace('agriculture', description='Agriculture data operations')

# Define models for documentation
commune_model = ns.model('Commune', {
    'id': fields.Integer(required=True, description='Commune ID'),
    'name': fields.String(required=True, description='Commune name'),
    'region_id': fields.Integer(required=True, description='Region ID'),
    'center_lat': fields.Float(description='Latitude of commune center'),
    'center_lon': fields.Float(description='Longitude of commune center'),
    'population': fields.Integer(description='Population'),
    'area_km2': fields.Float(description='Area in square kilometers'),
})

crop_model = ns.model('Crop', {
    'id': fields.Integer(required=True, description='Crop ID'),
    'name': fields.String(required=True, description='Crop name'),
    'name_fr': fields.String(description='French name'),
    'category': fields.String(description='Crop category'),
    'fao_code': fields.String(description='FAO code'),
})

agri_stats_model = ns.model('AgriStats', {
    'id': fields.Integer(required=True, description='Statistics ID'),
    'commune_id': fields.Integer(required=True, description='Commune ID'),
    'crop_id': fields.Integer(required=True, description='Crop ID'),
    'year': fields.Integer(required=True, description='Year'),
    'production_tonnes': fields.Float(description='Production in tonnes'),
    'yield_tonnes_per_ha': fields.Float(description='Yield per hectare'),
    'area_harvested_ha': fields.Float(description='Harvested area in hectares'),
    'price_per_kg': fields.Float(description='Price per kg'),
    'price_currency': fields.String(description='Currency code'),
})


@ns.route('/communes')
class CommuneList(Resource):
    """Commune list operations"""

    @ns.doc('list_communes')
    @ns.marshal_list_with(commune_model)
    def get(self):
        """List all communes - Public endpoint for landing page"""
        communes = Commune.query.all()
        return [c.to_dict() for c in communes]


@ns.route('/communes/<int:commune_id>')
@ns.param('commune_id', 'Commune identifier')
class CommuneDetail(Resource):
    """Commune detail operations"""

    @ns.doc('get_commune')
    @ns.marshal_with(commune_model)
    @require_api_key('agriculture:read')
    def get(self, commune_id):
        """Get commune by ID"""
        commune = Commune.get_by_id(commune_id)
        if not commune:
            ns.abort(404, f'Commune {commune_id} not found')
        return commune.to_dict()


@ns.route('/crops')
class CropList(Resource):
    """Crop list operations"""

    @ns.doc('list_crops')
    @ns.marshal_list_with(crop_model)
    @require_api_key('agriculture:read')
    def get(self):
        """List all crops"""
        crops = Crop.query.all()
        return [c.to_dict() for c in crops]


@ns.route('/crops/<int:crop_id>')
@ns.param('crop_id', 'Crop identifier')
class CropDetail(Resource):
    """Crop detail operations"""

    @ns.doc('get_crop')
    @ns.marshal_with(crop_model)
    @require_api_key('agriculture:read')
    def get(self, crop_id):
        """Get crop by ID"""
        crop = Crop.get_by_id(crop_id)
        if not crop:
            ns.abort(404, f'Crop {crop_id} not found')
        return crop.to_dict()


@ns.route('/index')
class AgricultureIndex(Resource):
    """Agriculture statistics index"""

    @ns.doc('get_agriculture_index')
    @ns.param('commune_id', 'Filter by commune ID', type='integer', required=False)
    @ns.param('crop_id', 'Filter by crop ID', type='integer', required=False)
    @ns.param('year', 'Filter by year', type='integer', required=False)
    @ns.param('year_from', 'Filter by year from', type='integer', required=False)
    @ns.param('year_to', 'Filter by year to', type='integer', required=False)
    @ns.param('page', 'Page number', type='integer', required=False, default=1)
    @ns.param('per_page', 'Items per page', type='integer', required=False, default=50)
    @require_api_key('agriculture:read')
    def get(self):
        """
        Get agriculture statistics with filters

        Returns paginated agriculture statistics based on filters
        """
        # Get query parameters
        commune_id = request.args.get('commune_id', type=int)
        crop_id = request.args.get('crop_id', type=int)
        year = request.args.get('year', type=int)
        year_from = request.args.get('year_from', type=int)
        year_to = request.args.get('year_to', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 500)  # Max 500 per page

        # Build query
        query = AgriStats.query

        # Apply filters
        filters = []
        if commune_id:
            filters.append(AgriStats.commune_id == commune_id)
        if crop_id:
            filters.append(AgriStats.crop_id == crop_id)
        if year:
            filters.append(AgriStats.year == year)
        if year_from:
            filters.append(AgriStats.year >= year_from)
        if year_to:
            filters.append(AgriStats.year <= year_to)

        if filters:
            query = query.filter(and_(*filters))

        # Order by year descending
        query = query.order_by(AgriStats.year.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Format response
        data = [stat.to_dict(include_relations=True) for stat in pagination.items]

        return {
            'data': data,
            'metadata': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'total_pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
            }
        }, 200


@ns.route('/index/<int:commune_id>/<int:crop_id>/<int:year>')
@ns.param('commune_id', 'Commune identifier')
@ns.param('crop_id', 'Crop identifier')
@ns.param('year', 'Year')
class AgricultureIndexDetail(Resource):
    """Agriculture statistics detail"""

    @ns.doc('get_agriculture_stat')
    @require_api_key('agriculture:read')
    def get(self, commune_id, crop_id, year):
        """Get specific agriculture statistic"""
        stat = AgriStats.query.filter_by(
            commune_id=commune_id,
            crop_id=crop_id,
            year=year
        ).first()

        if not stat:
            ns.abort(404, f'Statistics not found for commune {commune_id}, crop {crop_id}, year {year}')

        return {
            'data': stat.to_dict(include_relations=True),
            'metadata': {
                'source': stat.data_source.name if stat.data_source else 'Unknown',
                'updated_at': stat.updated_at.isoformat() if stat.updated_at else None
            }
        }, 200

@ns.route('/stats/aggregated')
class AggregatedStatistics(Resource):
    """Aggregated agriculture statistics with KPI calculations"""

    @ns.doc('get_aggregated_stats')
    @ns.param('commune_id', 'Filter by single commune ID', type='integer', required=False)
    @ns.param('commune_ids', 'Filter by multiple commune IDs (comma-separated)', type='string', required=False)
    @ns.param('crop_id', 'Filter by crop ID', type='integer', required=False)
    @ns.param('crop_ids', 'Filter by multiple crop IDs (comma-separated)', type='string', required=False)
    @ns.param('year_from', 'Start year (inclusive)', type='integer', required=False, default=2010)
    @ns.param('year_to', 'End year (inclusive)', type='integer', required=False)
    @ns.param('region_id', 'Filter by region ID', type='integer', required=False)
    @require_api_key('agriculture:read')
    def get(self):
        """
        Get aggregated agriculture statistics with KPIs and trends

        Calculates meaningful indices:
        - Total production by crop/commune
        - Average yield and price
        - Production trends over time
        - Regional aggregates
        - Year-over-year changes
        
        Perfect for dashboards and reporting.
        """
        # Parse parameters
        commune_id = request.args.get('commune_id', type=int)
        commune_ids_str = request.args.get('commune_ids', type=str)
        crop_id = request.args.get('crop_id', type=int)
        crop_ids_str = request.args.get('crop_ids', type=str)
        region_id = request.args.get('region_id', type=int)
        year_from = request.args.get('year_from', 2010, type=int)
        year_to = request.args.get('year_to', type=int)

        # Parse comma-separated IDs
        commune_ids = []
        if commune_id:
            commune_ids = [commune_id]
        elif commune_ids_str:
            try:
                commune_ids = [int(x.strip()) for x in commune_ids_str.split(',')]
            except ValueError:
                ns.abort(400, 'Invalid commune_ids format. Use comma-separated integers.')

        crop_ids = []
        if crop_id:
            crop_ids = [crop_id]
        elif crop_ids_str:
            try:
                crop_ids = [int(x.strip()) for x in crop_ids_str.split(',')]
            except ValueError:
                ns.abort(400, 'Invalid crop_ids format. Use comma-separated integers.')

        # Build base query
        query = AgriStats.query

        # Apply filters
        filters = [AgriStats.year >= year_from]
        
        if year_to:
            filters.append(AgriStats.year <= year_to)
        
        if commune_ids:
            filters.append(AgriStats.commune_id.in_(commune_ids))
        elif region_id:
            # Get communes in region
            region_communes = db.session.query(Commune.id).filter_by(region_id=region_id).all()
            region_commune_ids = [c[0] for c in region_communes]
            filters.append(AgriStats.commune_id.in_(region_commune_ids))
        
        if crop_ids:
            filters.append(AgriStats.crop_id.in_(crop_ids))

        if filters:
            query = query.filter(and_(*filters))

        stats = query.all()

        if not stats:
            return {
                'data': {
                    'summary': {},
                    'by_commune': [],
                    'by_crop': [],
                    'by_year': [],
                    'trends': {}
                },
                'metadata': {
                    'total_records': 0,
                    'year_from': year_from,
                    'year_to': year_to,
                    'filters_applied': {
                        'commune_id': commune_id,
                        'crop_id': crop_id,
                        'region_id': region_id
                    }
                }
            }, 200

        # === CALCULATE AGGREGATES ===
        
        # 1. OVERALL SUMMARY
        total_production = sum(s.production_tonnes or 0 for s in stats)
        total_area = sum(s.area_harvested_ha or 0 for s in stats)
        avg_yield = total_production / total_area if total_area > 0 else 0
        avg_price = mean([s.price_per_kg for s in stats if s.price_per_kg]) or 0
        avg_quality = mean([s.data_quality_score for s in stats if s.data_quality_score]) or 0
        data_count = len(stats)
        estimated_count = sum(1 for s in stats if s.is_estimated)
        estimated_pct = (estimated_count / data_count * 100) if data_count > 0 else 0

        summary = {
            'total_production_tonnes': round(total_production, 2),
            'total_area_ha': round(total_area, 2),
            'average_yield_t_ha': round(avg_yield, 2),
            'average_price_xof_kg': round(avg_price, 2),
            'average_quality_score': round(avg_quality, 3),
            'data_points': data_count,
            'estimated_data_pct': round(estimated_pct, 1),
        }

        # 2. AGGREGATION BY COMMUNE
        by_commune = {}
        for stat in stats:
            commune_key = stat.commune_id
            if commune_key not in by_commune:
                commune = stat.commune
                by_commune[commune_key] = {
                    'commune_id': commune_key,
                    'commune_name': commune.name if commune else 'Unknown',
                    'production_tonnes': 0,
                    'area_ha': 0,
                    'avg_yield': 0,
                    'avg_price': 0,
                    'records': 0,
                    'year_range': [None, None]
                }
            
            by_commune[commune_key]['production_tonnes'] += stat.production_tonnes or 0
            by_commune[commune_key]['area_ha'] += stat.area_harvested_ha or 0
            by_commune[commune_key]['records'] += 1
            
            # Track year range
            if by_commune[commune_key]['year_range'][0] is None or stat.year < by_commune[commune_key]['year_range'][0]:
                by_commune[commune_key]['year_range'][0] = stat.year
            if by_commune[commune_key]['year_range'][1] is None or stat.year > by_commune[commune_key]['year_range'][1]:
                by_commune[commune_key]['year_range'][1] = stat.year

        # Calculate averages for communes
        for commune_data in by_commune.values():
            if commune_data['area_ha'] > 0:
                commune_data['avg_yield'] = round(commune_data['production_tonnes'] / commune_data['area_ha'], 2)
            commune_data['production_tonnes'] = round(commune_data['production_tonnes'], 2)
            commune_data['area_ha'] = round(commune_data['area_ha'], 2)

        by_commune_list = sorted(by_commune.values(), key=lambda x: x['production_tonnes'], reverse=True)

        # 3. AGGREGATION BY CROP
        by_crop = {}
        for stat in stats:
            crop_key = stat.crop_id
            if crop_key not in by_crop:
                crop = stat.crop
                by_crop[crop_key] = {
                    'crop_id': crop_key,
                    'crop_name': crop.name if crop else 'Unknown',
                    'production_tonnes': 0,
                    'area_ha': 0,
                    'avg_yield': 0,
                    'avg_price': 0,
                    'records': 0
                }
            
            by_crop[crop_key]['production_tonnes'] += stat.production_tonnes or 0
            by_crop[crop_key]['area_ha'] += stat.area_harvested_ha or 0
            by_crop[crop_key]['avg_price'] += stat.price_per_kg or 0
            by_crop[crop_key]['records'] += 1

        # Calculate averages for crops
        for crop_data in by_crop.values():
            if crop_data['area_ha'] > 0:
                crop_data['avg_yield'] = round(crop_data['production_tonnes'] / crop_data['area_ha'], 2)
            if crop_data['records'] > 0:
                crop_data['avg_price'] = round(crop_data['avg_price'] / crop_data['records'], 2)
            crop_data['production_tonnes'] = round(crop_data['production_tonnes'], 2)
            crop_data['area_ha'] = round(crop_data['area_ha'], 2)

        by_crop_list = sorted(by_crop.values(), key=lambda x: x['production_tonnes'], reverse=True)

        # 4. AGGREGATION BY YEAR
        by_year = {}
        for stat in stats:
            year_key = stat.year
            if year_key not in by_year:
                by_year[year_key] = {
                    'year': year_key,
                    'production_tonnes': 0,
                    'area_ha': 0,
                    'avg_yield': 0,
                    'avg_price': 0,
                    'records': 0
                }
            
            by_year[year_key]['production_tonnes'] += stat.production_tonnes or 0
            by_year[year_key]['area_ha'] += stat.area_harvested_ha or 0
            by_year[year_key]['avg_price'] += stat.price_per_kg or 0
            by_year[year_key]['records'] += 1

        # Calculate averages for years
        for year_data in by_year.values():
            if year_data['area_ha'] > 0:
                year_data['avg_yield'] = round(year_data['production_tonnes'] / year_data['area_ha'], 2)
            if year_data['records'] > 0:
                year_data['avg_price'] = round(year_data['avg_price'] / year_data['records'], 2)
            year_data['production_tonnes'] = round(year_data['production_tonnes'], 2)
            year_data['area_ha'] = round(year_data['area_ha'], 2)

        by_year_list = sorted(by_year.values(), key=lambda x: x['year'])

        # 5. TREND ANALYSIS
        trends = {}
        if len(by_year_list) >= 2:
            first_year_data = by_year_list[0]
            last_year_data = by_year_list[-1]
            
            prod_change = last_year_data['production_tonnes'] - first_year_data['production_tonnes']
            prod_change_pct = (prod_change / first_year_data['production_tonnes'] * 100) if first_year_data['production_tonnes'] > 0 else 0
            
            yield_change = last_year_data['avg_yield'] - first_year_data['avg_yield']
            yield_change_pct = (yield_change / first_year_data['avg_yield'] * 100) if first_year_data['avg_yield'] > 0 else 0
            
            price_change = last_year_data['avg_price'] - first_year_data['avg_price']
            price_change_pct = (price_change / first_year_data['avg_price'] * 100) if first_year_data['avg_price'] > 0 else 0
            
            trends = {
                'period': f"{first_year_data['year']}-{last_year_data['year']}",
                'production_change_tonnes': round(prod_change, 2),
                'production_change_pct': round(prod_change_pct, 1),
                'yield_change_t_ha': round(yield_change, 2),
                'yield_change_pct': round(yield_change_pct, 1),
                'price_change_xof_kg': round(price_change, 2),
                'price_change_pct': round(price_change_pct, 1),
            }

        return {
            'data': {
                'summary': summary,
                'by_commune': by_commune_list,
                'by_crop': by_crop_list,
                'by_year': by_year_list,
                'trends': trends
            },
            'metadata': {
                'total_records': data_count,
                'year_from': year_from,
                'year_to': year_to,
                'filters_applied': {
                    'commune_id': commune_id,
                    'crop_id': crop_id,
                    'region_id': region_id
                }
            }
        }, 200