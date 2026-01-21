"""
Business API routes
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy import and_, func
import json

from app import db
from app.models.geo import Commune
from app.models.business import BusinessSector, BusinessStats
from app.utils.auth import require_api_key

# Create namespace
ns = Namespace('business', description='Business data operations')

# Define models for documentation
business_sector_model = ns.model('BusinessSector', {
    'id': fields.Integer(required=True, description='Business Sector ID'),
    'name': fields.String(required=True, description='Business sector name'),
    'name_fr': fields.String(description='French name'),
    'category': fields.String(description='Sector category'),
    'description': fields.String(description='Description'),
})

business_stats_model = ns.model('BusinessStats', {
    'id': fields.Integer(required=True, description='Statistics ID'),
    'commune_id': fields.Integer(required=True, description='Commune ID'),
    'sector_id': fields.Integer(required=True, description='Business Sector ID'),
    'year': fields.Integer(required=True, description='Year'),
    'quarter': fields.Integer(description='Quarter (1-4)'),
    'num_businesses': fields.Integer(description='Number of businesses'),
    'num_new_businesses': fields.Integer(description='New businesses'),
    'business_birth_rate': fields.Float(description='Business birth rate (%)'),
    'total_revenue': fields.Float(description='Total revenue'),
    'total_employees': fields.Integer(description='Total employees'),
    'formality_rate': fields.Float(description='Formality rate (%)'),
    'data_quality_score': fields.Float(description='Data quality score (0-1)'),
    # Labeling indices
    'business_density_index': fields.Float(description='Business density index (0-100)'),
    'sector_growth_score': fields.Float(description='Sector growth score (0-100)'),
    'economic_resilience_index': fields.Float(description='Economic resilience index (0-100)'),
    'market_gap_indicator': fields.Float(description='Market gap indicator (0-100)'),
    'competition_intensity': fields.String(description='Competition intensity'),
    'market_saturation': fields.String(description='Market saturation'),
})


@ns.route('/sectors')
class BusinessSectorList(Resource):
    """Business sector list operations"""

    @ns.doc('list_business_sectors')
    @ns.marshal_list_with(business_sector_model)
    @require_api_key('business:read')
    def get(self):
        """List all business sectors"""
        business_sectors = BusinessSector.query.all()
        return [bs.to_dict() for bs in business_sectors]


@ns.route('/sectors/<int:sector_id>')
@ns.param('sector_id', 'Business sector identifier')
class BusinessSectorDetail(Resource):
    """Business sector detail operations"""

    @ns.doc('get_business_sector')
    @ns.marshal_with(business_sector_model)
    @require_api_key('business:read')
    def get(self, sector_id):
        """Get business sector by ID"""
        sector = BusinessSector.get_by_id(sector_id)
        if not sector:
            ns.abort(404, f'Business sector {sector_id} not found')
        return sector.to_dict()


@ns.route('/index')
class BusinessIndex(Resource):
    """Business statistics index"""

    @ns.doc('get_business_index')
    @ns.param('commune_id', 'Filter by commune ID', type='integer', required=False)
    @ns.param('sector_id', 'Filter by business sector ID', type='integer', required=False)
    @ns.param('year', 'Filter by year', type='integer', required=False)
    @ns.param('year_from', 'Filter by year from', type='integer', required=False)
    @ns.param('year_to', 'Filter by year to', type='integer', required=False)
    @ns.param('quarter', 'Filter by quarter (1-4)', type='integer', required=False)
    @ns.param('category', 'Filter by sector category', type='string', required=False)
    @ns.param('market_saturation', 'Filter by market saturation', type='string', required=False)
    @ns.param('page', 'Page number', type='integer', required=False, default=1)
    @ns.param('per_page', 'Items per page', type='integer', required=False, default=50)
    @require_api_key('business:read')
    def get(self):
        """
        Get business statistics with filters

        Returns paginated business statistics based on filters
        """
        # Get query parameters
        commune_id = request.args.get('commune_id', type=int)
        sector_id = request.args.get('sector_id', type=int)
        year = request.args.get('year', type=int)
        year_from = request.args.get('year_from', type=int)
        year_to = request.args.get('year_to', type=int)
        quarter = request.args.get('quarter', type=int)
        market_saturation = request.args.get('market_saturation', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 500)  # Max 500 per page

        # Build query
        query = BusinessStats.query

        # Apply filters
        filters = []
        if commune_id:
            filters.append(BusinessStats.commune_id == commune_id)
        if sector_id:
            filters.append(BusinessStats.sector_id == sector_id)
        if year:
            filters.append(BusinessStats.year == year)
        if year_from:
            filters.append(BusinessStats.year >= year_from)
        if year_to:
            filters.append(BusinessStats.year <= year_to)
        if quarter:
            filters.append(BusinessStats.quarter == quarter)
        if market_saturation:
            filters.append(BusinessStats.market_saturation == market_saturation)

        if filters:
            query = query.filter(and_(*filters))

        # Order by year and quarter descending
        query = query.order_by(BusinessStats.year.desc(), BusinessStats.quarter.desc())

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
class BusinessStatsDetail(Resource):
    """Business statistics detail"""

    @ns.doc('get_business_stat')
    @require_api_key('business:read')
    def get(self, stat_id):
        """Get specific business statistic with multi-source information"""
        stat = BusinessStats.get_by_id(stat_id)

        if not stat:
            ns.abort(404, f'Business statistic {stat_id} not found')

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
class BusinessAggregatedStats(Resource):
    """Aggregated Business statistics for analytics"""

    @ns.doc('get_business_aggregated')
    @ns.param('year_from', 'Filter from year', type='integer', required=False)
    @ns.param('year_to', 'Filter to year', type='integer', required=False)
    @ns.param('commune_id', 'Filter by commune ID', type='integer', required=False)
    @ns.param('sector_id', 'Filter by business sector ID', type='integer', required=False)
    @ns.param('region_id', 'Filter by region ID', type='integer', required=False)
    @ns.param('group_by', 'Group results by: commune, sector, year, or none', type='string', required=False)
    @require_api_key('business:read')
    def get(self):
        """
        Get aggregated business statistics for analytics and visualization

        Supports flexible filtering and grouping for KPI calculations
        """
        # Get parameters
        year_from = request.args.get('year_from', 2010, type=int)
        year_to = request.args.get('year_to', 2024, type=int)
        commune_id = request.args.get('commune_id', type=int)
        sector_id = request.args.get('sector_id', type=int)
        region_id = request.args.get('region_id', type=int)
        group_by = request.args.get('group_by', 'none', type=str)

        # Start with base query joining with commune for region filtering
        query = db.session.query(
            BusinessStats,
            Commune.name.label('commune_name'),
            BusinessSector.name.label('sector_name')
        ).join(Commune, BusinessStats.commune_id == Commune.id)\
         .join(BusinessSector, BusinessStats.sector_id == BusinessSector.id)

        # Apply filters
        filters = [
            BusinessStats.year >= year_from,
            BusinessStats.year <= year_to,
        ]

        if commune_id:
            filters.append(BusinessStats.commune_id == commune_id)
        if sector_id:
            filters.append(BusinessStats.sector_id == sector_id)
        if region_id:
            filters.append(Commune.region_id == region_id)

        query = query.filter(and_(*filters))

        # Execute query
        results = query.all()

        # Process results based on grouping
        if group_by == 'commune':
            return self._aggregate_by_commune(results), 200
        elif group_by == 'sector':
            return self._aggregate_by_sector(results), 200
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
                    'total_businesses': 0,
                    'total_revenue': 0,
                    'total_employees': 0,
                    'avg_birth_rate': 0,
                    'avg_formality_rate': 0,
                    'data_quality_avg': 0
                },
                'metadata': {'total_records': 0}
            }

        stats = [r[0] for r in results]
        
        # Calculate KPIs
        businesses = [s.num_businesses for s in stats if s.num_businesses]
        revenues = [s.total_revenue for s in stats if s.total_revenue and s.total_revenue > 0]
        employees = [s.total_employees for s in stats if s.total_employees]
        birth_rates = [s.business_birth_rate for s in stats if s.business_birth_rate]
        formal_rates = [s.formality_rate for s in stats if s.formality_rate]
        qualities = [s.data_quality_score for s in stats if s.data_quality_score]
        
        kpis = {
            'total_businesses': sum(businesses) if businesses else 0,
            'total_revenue': sum(revenues) if revenues else 0,
            'total_employees': sum(employees) if employees else 0,
            'avg_birth_rate': sum(birth_rates) / len(birth_rates) if birth_rates else 0,
            'avg_formality_rate': sum(formal_rates) / len(formal_rates) if formal_rates else 0,
            'data_quality_avg': sum(qualities) / len(qualities) if qualities else 0
        }

        return {
            'kpis': kpis,
            'metadata': {
                'total_records': len(stats),
                'year_range': (min([s.year for s in stats]), max([s.year for s in stats])),
                'num_communes': len(set([s.commune_id for s in stats])),
                'num_sectors': len(set([s.sector_id for s in stats]))
            }
        }

    def _aggregate_by_commune(self, results):
        """Aggregate statistics by commune"""
        by_commune = {}
        
        for stat, commune_name, sector_name in results:
            commune_id = stat.commune_id
            if commune_id not in by_commune:
                by_commune[commune_id] = {
                    'commune_id': commune_id,
                    'commune_name': commune_name,
                    'businesses': [],
                    'revenues': [],
                    'employees': [],
                    'birth_rates': [],
                    'formal_rates': [],
                    'quality_scores': []
                }
            
            if stat.num_businesses:
                by_commune[commune_id]['businesses'].append(stat.num_businesses)
            if stat.total_revenue and stat.total_revenue > 0:
                by_commune[commune_id]['revenues'].append(stat.total_revenue)
            if stat.total_employees:
                by_commune[commune_id]['employees'].append(stat.total_employees)
            if stat.business_birth_rate:
                by_commune[commune_id]['birth_rates'].append(stat.business_birth_rate)
            if stat.formality_rate:
                by_commune[commune_id]['formal_rates'].append(stat.formality_rate)
            if stat.data_quality_score:
                by_commune[commune_id]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for commune_id, data in by_commune.items():
            agg = {
                'commune_id': data['commune_id'],
                'commune_name': data['commune_name'],
                'total_businesses': sum(data['businesses']) if data['businesses'] else 0,
                'total_revenue': sum(data['revenues']) if data['revenues'] else 0,
                'total_employees': sum(data['employees']) if data['employees'] else 0,
                'avg_birth_rate': sum(data['birth_rates']) / len(data['birth_rates']) if data['birth_rates'] else 0,
                'avg_formality_rate': sum(data['formal_rates']) / len(data['formal_rates']) if data['formal_rates'] else 0,
                'data_quality': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            }
            aggregated.append(agg)

        # Sort by num businesses
        aggregated.sort(key=lambda x: x['total_businesses'], reverse=True)
        
        return {
            'data': aggregated,
            'metadata': {
                'group_by': 'commune',
                'total_communes': len(aggregated),
                'records': len(results)
            }
        }

    def _aggregate_by_sector(self, results):
        """Aggregate statistics by business sector"""
        by_sector = {}
        
        for stat, commune_name, sector_name in results:
            sector_id = stat.sector_id
            if sector_id not in by_sector:
                by_sector[sector_id] = {
                    'sector_id': sector_id,
                    'sector_name': sector_name,
                    'businesses': [],
                    'revenues': [],
                    'employees': [],
                    'birth_rates': [],
                    'formal_rates': [],
                    'quality_scores': []
                }
            
            if stat.num_businesses:
                by_sector[sector_id]['businesses'].append(stat.num_businesses)
            if stat.total_revenue and stat.total_revenue > 0:
                by_sector[sector_id]['revenues'].append(stat.total_revenue)
            if stat.total_employees:
                by_sector[sector_id]['employees'].append(stat.total_employees)
            if stat.business_birth_rate:
                by_sector[sector_id]['birth_rates'].append(stat.business_birth_rate)
            if stat.formality_rate:
                by_sector[sector_id]['formal_rates'].append(stat.formality_rate)
            if stat.data_quality_score:
                by_sector[sector_id]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for sector_id, data in by_sector.items():
            agg = {
                'sector_id': data['sector_id'],
                'sector_name': data['sector_name'],
                'total_businesses': sum(data['businesses']) if data['businesses'] else 0,
                'total_revenue': sum(data['revenues']) if data['revenues'] else 0,
                'total_employees': sum(data['employees']) if data['employees'] else 0,
                'avg_birth_rate': sum(data['birth_rates']) / len(data['birth_rates']) if data['birth_rates'] else 0,
                'avg_formality_rate': sum(data['formal_rates']) / len(data['formal_rates']) if data['formal_rates'] else 0,
                'data_quality': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            }
            aggregated.append(agg)

        aggregated.sort(key=lambda x: x['total_businesses'], reverse=True)
        
        return {
            'data': aggregated,
            'metadata': {
                'group_by': 'sector',
                'total_sectors': len(aggregated),
                'records': len(results)
            }
        }

    def _aggregate_by_year(self, results):
        """Aggregate statistics by year"""
        by_year = {}
        
        for stat, commune_name, sector_name in results:
            year = stat.year
            if year not in by_year:
                by_year[year] = {
                    'year': year,
                    'businesses': [],
                    'revenues': [],
                    'employees': [],
                    'birth_rates': [],
                    'formal_rates': [],
                    'quality_scores': []
                }
            
            if stat.num_businesses:
                by_year[year]['businesses'].append(stat.num_businesses)
            if stat.total_revenue and stat.total_revenue > 0:
                by_year[year]['revenues'].append(stat.total_revenue)
            if stat.total_employees:
                by_year[year]['employees'].append(stat.total_employees)
            if stat.business_birth_rate:
                by_year[year]['birth_rates'].append(stat.business_birth_rate)
            if stat.formality_rate:
                by_year[year]['formal_rates'].append(stat.formality_rate)
            if stat.data_quality_score:
                by_year[year]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for year in sorted(by_year.keys()):
            data = by_year[year]
            agg = {
                'year': data['year'],
                'total_businesses': sum(data['businesses']) if data['businesses'] else 0,
                'total_revenue': sum(data['revenues']) if data['revenues'] else 0,
                'total_employees': sum(data['employees']) if data['employees'] else 0,
                'avg_birth_rate': sum(data['birth_rates']) / len(data['birth_rates']) if data['birth_rates'] else 0,
                'avg_formality_rate': sum(data['formal_rates']) / len(data['formal_rates']) if data['formal_rates'] else 0,
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
