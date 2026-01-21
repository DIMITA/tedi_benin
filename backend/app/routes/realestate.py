"""
Real Estate API routes
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy import and_, func
import json

from app import db
from app.models.geo import Commune
from app.models.realestate import PropertyType, RealEstateStats
from app.utils.auth import require_api_key

# Create namespace
ns = Namespace('realestate', description='Real Estate data operations')

# Define models for documentation
property_type_model = ns.model('PropertyType', {
    'id': fields.Integer(required=True, description='Property Type ID'),
    'name': fields.String(required=True, description='Property type name'),
    'name_fr': fields.String(description='French name'),
    'category': fields.String(description='Property category'),
    'description': fields.String(description='Description'),
})

real_estate_stats_model = ns.model('RealEstateStats', {
    'id': fields.Integer(required=True, description='Statistics ID'),
    'commune_id': fields.Integer(required=True, description='Commune ID'),
    'property_type_id': fields.Integer(required=True, description='Property Type ID'),
    'year': fields.Integer(required=True, description='Year'),
    'quarter': fields.Integer(description='Quarter (1-4)'),
    'median_price': fields.Float(description='Median property price'),
    'price_per_sqm': fields.Float(description='Price per square meter'),
    'num_transactions': fields.Integer(description='Number of transactions'),
    'data_quality_score': fields.Float(description='Data quality score (0-1)'),
    # Labeling indices
    'geo_zone': fields.String(description='Geographic zone'),
    'price_per_sqm_index': fields.Float(description='Price per sqm index (0-100)'),
    'price_trend': fields.String(description='Price trend'),
    'land_risk_level': fields.String(description='Land risk level'),
    'infrastructure_score': fields.Float(description='Infrastructure score (0-100)'),
    'legal_clarity_index': fields.Float(description='Legal clarity index (0-100)'),
    'development_potential': fields.String(description='Development potential'),
})


@ns.route('/property-types')
class PropertyTypeList(Resource):
    """Property type list operations"""

    @ns.doc('list_property_types')
    @ns.marshal_list_with(property_type_model)
    @require_api_key('realestate:read')
    def get(self):
        """List all property types"""
        property_types = PropertyType.query.all()
        return [pt.to_dict() for pt in property_types]


@ns.route('/property-types/<int:property_type_id>')
@ns.param('property_type_id', 'Property type identifier')
class PropertyTypeDetail(Resource):
    """Property type detail operations"""

    @ns.doc('get_property_type')
    @ns.marshal_with(property_type_model)
    @require_api_key('realestate:read')
    def get(self, property_type_id):
        """Get property type by ID"""
        property_type = PropertyType.get_by_id(property_type_id)
        if not property_type:
            ns.abort(404, f'Property type {property_type_id} not found')
        return property_type.to_dict()


@ns.route('/index')
class RealEstateIndex(Resource):
    """Real Estate statistics index"""

    @ns.doc('get_realestate_index')
    @ns.param('commune_id', 'Filter by commune ID', type='integer', required=False)
    @ns.param('property_type_id', 'Filter by property type ID', type='integer', required=False)
    @ns.param('year', 'Filter by year', type='integer', required=False)
    @ns.param('year_from', 'Filter by year from', type='integer', required=False)
    @ns.param('year_to', 'Filter by year to', type='integer', required=False)
    @ns.param('quarter', 'Filter by quarter (1-4)', type='integer', required=False)
    @ns.param('geo_zone', 'Filter by geographic zone', type='string', required=False)
    @ns.param('price_trend', 'Filter by price trend', type='string', required=False)
    @ns.param('page', 'Page number', type='integer', required=False, default=1)
    @ns.param('per_page', 'Items per page', type='integer', required=False, default=50)
    @require_api_key('realestate:read')
    def get(self):
        """
        Get real estate statistics with filters

        Returns paginated real estate statistics based on filters
        """
        # Get query parameters
        commune_id = request.args.get('commune_id', type=int)
        property_type_id = request.args.get('property_type_id', type=int)
        year = request.args.get('year', type=int)
        year_from = request.args.get('year_from', type=int)
        year_to = request.args.get('year_to', type=int)
        quarter = request.args.get('quarter', type=int)
        geo_zone = request.args.get('geo_zone', type=str)
        price_trend = request.args.get('price_trend', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 500)  # Max 500 per page

        # Build query
        query = RealEstateStats.query

        # Apply filters
        filters = []
        if commune_id:
            filters.append(RealEstateStats.commune_id == commune_id)
        if property_type_id:
            filters.append(RealEstateStats.property_type_id == property_type_id)
        if year:
            filters.append(RealEstateStats.year == year)
        if year_from:
            filters.append(RealEstateStats.year >= year_from)
        if year_to:
            filters.append(RealEstateStats.year <= year_to)
        if quarter:
            filters.append(RealEstateStats.quarter == quarter)
        if geo_zone:
            filters.append(RealEstateStats.geo_zone == geo_zone)
        if price_trend:
            filters.append(RealEstateStats.price_trend == price_trend)

        if filters:
            query = query.filter(and_(*filters))

        # Order by year and quarter descending
        query = query.order_by(RealEstateStats.year.desc(), RealEstateStats.quarter.desc())

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


@ns.route('/stats/<int:stat_id>')
@ns.param('stat_id', 'Statistic identifier')
class RealEstateStatsDetail(Resource):
    """Real Estate statistics detail"""

    @ns.doc('get_realestate_stat')
    @require_api_key('realestate:read')
    def get(self, stat_id):
        """Get specific real estate statistic with multi-source information"""
        stat = RealEstateStats.get_by_id(stat_id)

        if not stat:
            ns.abort(404, f'Real estate statistic {stat_id} not found')

        # Get source contributions if any
        source_contributions = []
        if hasattr(stat, 'source_contributions') and stat.source_contributions:
            for contrib in stat.source_contributions:
                source_contributions.append({
                    'source_id': contrib.data_source_id,
                    'source_name': contrib.data_source.name if contrib.data_source else 'Unknown',
                    'contribution_weight': contrib.contribution_weight,
                    'confidence_score': contrib.confidence_score,
                    'is_primary': contrib.is_primary,
                    'source_value': contrib.source_value,
                    'deviation_from_final': contrib.deviation_from_final
                })

        return {
            'data': stat.to_dict(include_relations=True),
            'metadata': {
                'primary_source': stat.data_source.name if stat.data_source else 'Unknown',
                'updated_at': stat.updated_at.isoformat() if stat.updated_at else None,
                'num_sources': len(source_contributions),
                'source_contributions': source_contributions
            }
        }, 200


@ns.route('/stats/aggregated')
class RealEstateAggregatedStats(Resource):
    """Aggregated Real Estate statistics for analytics"""

    @ns.doc('get_realestate_aggregated')
    @ns.param('year_from', 'Filter from year', type='integer', required=False)
    @ns.param('year_to', 'Filter to year', type='integer', required=False)
    @ns.param('commune_id', 'Filter by commune ID', type='integer', required=False)
    @ns.param('property_type_id', 'Filter by property type ID', type='integer', required=False)
    @ns.param('region_id', 'Filter by region ID', type='integer', required=False)
    @ns.param('group_by', 'Group results by: commune, property_type, year, or none', type='string', required=False)
    @require_api_key('realestate:read')
    def get(self):
        """
        Get aggregated real estate statistics for analytics and visualization

        Supports flexible filtering and grouping for KPI calculations
        """
        # Get parameters
        year_from = request.args.get('year_from', 2010, type=int)
        year_to = request.args.get('year_to', 2024, type=int)
        commune_id = request.args.get('commune_id', type=int)
        property_type_id = request.args.get('property_type_id', type=int)
        region_id = request.args.get('region_id', type=int)
        group_by = request.args.get('group_by', 'none', type=str)

        # Start with base query joining with commune for region filtering
        query = db.session.query(
            RealEstateStats,
            Commune.name.label('commune_name'),
            PropertyType.name.label('property_type_name')
        ).join(Commune, RealEstateStats.commune_id == Commune.id)\
         .join(PropertyType, RealEstateStats.property_type_id == PropertyType.id)

        # Apply filters
        filters = [
            RealEstateStats.year >= year_from,
            RealEstateStats.year <= year_to,
        ]

        if commune_id:
            filters.append(RealEstateStats.commune_id == commune_id)
        if property_type_id:
            filters.append(RealEstateStats.property_type_id == property_type_id)
        if region_id:
            filters.append(Commune.region_id == region_id)

        query = query.filter(and_(*filters))

        # Execute query
        results = query.all()

        # Process results based on grouping
        if group_by == 'commune':
            return self._aggregate_by_commune(results), 200
        elif group_by == 'property_type':
            return self._aggregate_by_property_type(results), 200
        elif group_by == 'year':
            return self._aggregate_by_year(results), 200
        else:
            # No grouping - return overall KPIs
            return self._calculate_overall_kpis(results), 200

    def _calculate_overall_kpis(self, results):
        """Calculate overall KPIs from all results"""
        if not results:
            return {
                'kpis': {
                    'avg_median_price': 0,
                    'avg_price_per_sqm': 0,
                    'total_transactions': 0,
                    'avg_rental_yield': 0,
                    'data_quality_avg': 0
                },
                'metadata': {'total_records': 0}
            }

        stats = [r[0] for r in results]
        
        # Calculate KPIs
        prices = [s.median_price for s in stats if s.median_price]
        price_sqm = [s.price_per_sqm for s in stats if s.price_per_sqm]
        yields = [s.rental_yield for s in stats if s.rental_yield and s.rental_yield > 0]
        qualities = [s.data_quality_score for s in stats if s.data_quality_score]
        
        kpis = {
            'avg_median_price': sum(prices) / len(prices) if prices else 0,
            'avg_price_per_sqm': sum(price_sqm) / len(price_sqm) if price_sqm else 0,
            'total_transactions': sum([s.num_transactions or 0 for s in stats]),
            'avg_rental_yield': sum(yields) / len(yields) if yields else 0,
            'data_quality_avg': sum(qualities) / len(qualities) if qualities else 0
        }

        return {
            'kpis': kpis,
            'metadata': {
                'total_records': len(stats),
                'year_range': (min([s.year for s in stats]), max([s.year for s in stats])),
                'num_communes': len(set([s.commune_id for s in stats])),
                'num_property_types': len(set([s.property_type_id for s in stats]))
            }
        }

    def _aggregate_by_commune(self, results):
        """Aggregate statistics by commune"""
        by_commune = {}
        
        for stat, commune_name, property_type_name in results:
            commune_id = stat.commune_id
            if commune_id not in by_commune:
                by_commune[commune_id] = {
                    'commune_id': commune_id,
                    'commune_name': commune_name,
                    'median_prices': [],
                    'price_sqm': [],
                    'transactions': [],
                    'rental_yields': [],
                    'quality_scores': []
                }
            
            if stat.median_price:
                by_commune[commune_id]['median_prices'].append(stat.median_price)
            if stat.price_per_sqm:
                by_commune[commune_id]['price_sqm'].append(stat.price_per_sqm)
            if stat.num_transactions:
                by_commune[commune_id]['transactions'].append(stat.num_transactions)
            if stat.rental_yield and stat.rental_yield > 0:
                by_commune[commune_id]['rental_yields'].append(stat.rental_yield)
            if stat.data_quality_score:
                by_commune[commune_id]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for commune_id, data in by_commune.items():
            agg = {
                'commune_id': data['commune_id'],
                'commune_name': data['commune_name'],
                'avg_median_price': sum(data['median_prices']) / len(data['median_prices']) if data['median_prices'] else 0,
                'avg_price_per_sqm': sum(data['price_sqm']) / len(data['price_sqm']) if data['price_sqm'] else 0,
                'total_transactions': sum(data['transactions']),
                'avg_rental_yield': sum(data['rental_yields']) / len(data['rental_yields']) if data['rental_yields'] else 0,
                'data_quality': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            }
            aggregated.append(agg)

        # Sort by transaction count
        aggregated.sort(key=lambda x: x['total_transactions'], reverse=True)
        
        return {
            'data': aggregated,
            'metadata': {
                'group_by': 'commune',
                'total_communes': len(aggregated),
                'records': len(results)
            }
        }

    def _aggregate_by_property_type(self, results):
        """Aggregate statistics by property type"""
        by_type = {}
        
        for stat, commune_name, property_type_name in results:
            prop_type_id = stat.property_type_id
            if prop_type_id not in by_type:
                by_type[prop_type_id] = {
                    'property_type_id': prop_type_id,
                    'property_type_name': property_type_name,
                    'median_prices': [],
                    'price_sqm': [],
                    'transactions': [],
                    'rental_yields': [],
                    'quality_scores': []
                }
            
            if stat.median_price:
                by_type[prop_type_id]['median_prices'].append(stat.median_price)
            if stat.price_per_sqm:
                by_type[prop_type_id]['price_sqm'].append(stat.price_per_sqm)
            if stat.num_transactions:
                by_type[prop_type_id]['transactions'].append(stat.num_transactions)
            if stat.rental_yield and stat.rental_yield > 0:
                by_type[prop_type_id]['rental_yields'].append(stat.rental_yield)
            if stat.data_quality_score:
                by_type[prop_type_id]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for prop_type_id, data in by_type.items():
            agg = {
                'property_type_id': data['property_type_id'],
                'property_type_name': data['property_type_name'],
                'avg_median_price': sum(data['median_prices']) / len(data['median_prices']) if data['median_prices'] else 0,
                'avg_price_per_sqm': sum(data['price_sqm']) / len(data['price_sqm']) if data['price_sqm'] else 0,
                'total_transactions': sum(data['transactions']),
                'avg_rental_yield': sum(data['rental_yields']) / len(data['rental_yields']) if data['rental_yields'] else 0,
                'data_quality': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            }
            aggregated.append(agg)

        aggregated.sort(key=lambda x: x['total_transactions'], reverse=True)
        
        return {
            'data': aggregated,
            'metadata': {
                'group_by': 'property_type',
                'total_types': len(aggregated),
                'records': len(results)
            }
        }

    def _aggregate_by_year(self, results):
        """Aggregate statistics by year"""
        by_year = {}
        
        for stat, commune_name, property_type_name in results:
            year = stat.year
            if year not in by_year:
                by_year[year] = {
                    'year': year,
                    'median_prices': [],
                    'price_sqm': [],
                    'transactions': [],
                    'rental_yields': [],
                    'quality_scores': []
                }
            
            if stat.median_price:
                by_year[year]['median_prices'].append(stat.median_price)
            if stat.price_per_sqm:
                by_year[year]['price_sqm'].append(stat.price_per_sqm)
            if stat.num_transactions:
                by_year[year]['transactions'].append(stat.num_transactions)
            if stat.rental_yield and stat.rental_yield > 0:
                by_year[year]['rental_yields'].append(stat.rental_yield)
            if stat.data_quality_score:
                by_year[year]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for year in sorted(by_year.keys()):
            data = by_year[year]
            agg = {
                'year': data['year'],
                'avg_median_price': sum(data['median_prices']) / len(data['median_prices']) if data['median_prices'] else 0,
                'avg_price_per_sqm': sum(data['price_sqm']) / len(data['price_sqm']) if data['price_sqm'] else 0,
                'total_transactions': sum(data['transactions']),
                'avg_rental_yield': sum(data['rental_yields']) / len(data['rental_yields']) if data['rental_yields'] else 0,
                'data_quality': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            }
            aggregated.append(agg)
        
        return {
            'data': aggregated,
            'metadata': {
                'group_by': 'year',
                'total_years': len(aggregated),
                'records': len(results)
            }
        }
