"""
Employment API routes
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy import and_, func
import json

from app import db
from app.models.geo import Commune
from app.models.employment import JobCategory, EmploymentStats
from app.utils.auth import require_api_key

# Create namespace
ns = Namespace('employment', description='Employment data operations')

# Define models for documentation
job_category_model = ns.model('JobCategory', {
    'id': fields.Integer(required=True, description='Job Category ID'),
    'name': fields.String(required=True, description='Job category name'),
    'name_fr': fields.String(description='French name'),
    'sector': fields.String(description='Economic sector'),
    'description': fields.String(description='Description'),
})

employment_stats_model = ns.model('EmploymentStats', {
    'id': fields.Integer(required=True, description='Statistics ID'),
    'commune_id': fields.Integer(required=True, description='Commune ID'),
    'job_category_id': fields.Integer(required=True, description='Job Category ID'),
    'year': fields.Integer(required=True, description='Year'),
    'quarter': fields.Integer(description='Quarter (1-4)'),
    'total_employed': fields.Integer(description='Total employed'),
    'total_unemployed': fields.Integer(description='Total unemployed'),
    'unemployment_rate': fields.Float(description='Unemployment rate (%)'),
    'informal_rate': fields.Float(description='Informality rate (%)'),
    'median_salary': fields.Float(description='Median monthly salary'),
    'data_quality_score': fields.Float(description='Data quality score (0-1)'),
    # Labeling indices
    'skill_level_index': fields.Float(description='Skill level index (0-100)'),
    'employment_pressure_index': fields.Float(description='Employment pressure index (0-100)'),
    'informality_rate_index': fields.Float(description='Informality rate index (0-100%)'),
    'salary_range_estimation': fields.String(description='Salary range estimation'),
})


@ns.route('/categories')
class JobCategoryList(Resource):
    """Job category list operations"""

    @ns.doc('list_job_categories')
    @ns.marshal_list_with(job_category_model)
    @require_api_key('employment:read')
    def get(self):
        """List all job categories"""
        job_categories = JobCategory.query.all()
        return [jc.to_dict() for jc in job_categories]


@ns.route('/categories/<int:category_id>')
@ns.param('category_id', 'Job category identifier')
class JobCategoryDetail(Resource):
    """Job category detail operations"""

    @ns.doc('get_job_category')
    @ns.marshal_with(job_category_model)
    @require_api_key('employment:read')
    def get(self, category_id):
        """Get job category by ID"""
        category = JobCategory.get_by_id(category_id)
        if not category:
            ns.abort(404, f'Job category {category_id} not found')
        return category.to_dict()


@ns.route('/index')
class EmploymentIndex(Resource):
    """Employment statistics index"""

    @ns.doc('get_employment_index')
    @ns.param('commune_id', 'Filter by commune ID', type='integer', required=False)
    @ns.param('job_category_id', 'Filter by job category ID', type='integer', required=False)
    @ns.param('year', 'Filter by year', type='integer', required=False)
    @ns.param('year_from', 'Filter by year from', type='integer', required=False)
    @ns.param('year_to', 'Filter by year to', type='integer', required=False)
    @ns.param('quarter', 'Filter by quarter (1-4)', type='integer', required=False)
    @ns.param('sector', 'Filter by economic sector', type='string', required=False)
    @ns.param('salary_range', 'Filter by salary range', type='string', required=False)
    @ns.param('page', 'Page number', type='integer', required=False, default=1)
    @ns.param('per_page', 'Items per page', type='integer', required=False, default=50)
    @require_api_key('employment:read')
    def get(self):
        """
        Get employment statistics with filters

        Returns paginated employment statistics based on filters
        """
        # Get query parameters
        commune_id = request.args.get('commune_id', type=int)
        job_category_id = request.args.get('job_category_id', type=int)
        year = request.args.get('year', type=int)
        year_from = request.args.get('year_from', type=int)
        year_to = request.args.get('year_to', type=int)
        quarter = request.args.get('quarter', type=int)
        salary_range = request.args.get('salary_range', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 500)  # Max 500 per page

        # Build query
        query = EmploymentStats.query

        # Apply filters
        filters = []
        if commune_id:
            filters.append(EmploymentStats.commune_id == commune_id)
        if job_category_id:
            filters.append(EmploymentStats.job_category_id == job_category_id)
        if year:
            filters.append(EmploymentStats.year == year)
        if year_from:
            filters.append(EmploymentStats.year >= year_from)
        if year_to:
            filters.append(EmploymentStats.year <= year_to)
        if quarter:
            filters.append(EmploymentStats.quarter == quarter)
        if salary_range:
            filters.append(EmploymentStats.salary_range_estimation == salary_range)

        if filters:
            query = query.filter(and_(*filters))

        # Order by year and quarter descending
        query = query.order_by(EmploymentStats.year.desc(), EmploymentStats.quarter.desc())

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
class EmploymentStatsDetail(Resource):
    """Employment statistics detail"""

    @ns.doc('get_employment_stat')
    @require_api_key('employment:read')
    def get(self, stat_id):
        """Get specific employment statistic with multi-source information"""
        stat = EmploymentStats.get_by_id(stat_id)

        if not stat:
            ns.abort(404, f'Employment statistic {stat_id} not found')

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
class EmploymentAggregatedStats(Resource):
    """Aggregated Employment statistics for analytics"""

    @ns.doc('get_employment_aggregated')
    @ns.param('year_from', 'Filter from year', type='integer', required=False)
    @ns.param('year_to', 'Filter to year', type='integer', required=False)
    @ns.param('commune_id', 'Filter by commune ID', type='integer', required=False)
    @ns.param('job_category_id', 'Filter by job category ID', type='integer', required=False)
    @ns.param('region_id', 'Filter by region ID', type='integer', required=False)
    @ns.param('group_by', 'Group results by: commune, job_category, year, or none', type='string', required=False)
    @require_api_key('employment:read')
    def get(self):
        """
        Get aggregated employment statistics for analytics and visualization

        Supports flexible filtering and grouping for KPI calculations
        """
        # Get parameters
        year_from = request.args.get('year_from', 2010, type=int)
        year_to = request.args.get('year_to', 2024, type=int)
        commune_id = request.args.get('commune_id', type=int)
        job_category_id = request.args.get('job_category_id', type=int)
        region_id = request.args.get('region_id', type=int)
        group_by = request.args.get('group_by', 'none', type=str)

        # Start with base query joining with commune for region filtering
        query = db.session.query(
            EmploymentStats,
            Commune.name.label('commune_name'),
            JobCategory.name.label('job_category_name')
        ).join(Commune, EmploymentStats.commune_id == Commune.id)\
         .join(JobCategory, EmploymentStats.job_category_id == JobCategory.id)

        # Apply filters
        filters = [
            EmploymentStats.year >= year_from,
            EmploymentStats.year <= year_to,
        ]

        if commune_id:
            filters.append(EmploymentStats.commune_id == commune_id)
        if job_category_id:
            filters.append(EmploymentStats.job_category_id == job_category_id)
        if region_id:
            filters.append(Commune.region_id == region_id)

        query = query.filter(and_(*filters))

        # Execute query
        results = query.all()

        # Process results based on grouping
        if group_by == 'commune':
            return self._aggregate_by_commune(results), 200
        elif group_by == 'job_category':
            return self._aggregate_by_job_category(results), 200
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
                    'total_employed': 0,
                    'avg_unemployment_rate': 0,
                    'avg_informal_rate': 0,
                    'avg_median_salary': 0,
                    'data_quality_avg': 0
                },
                'metadata': {'total_records': 0}
            }

        stats = [r[0] for r in results]
        
        # Calculate KPIs
        employed = [s.total_employed for s in stats if s.total_employed]
        unemp_rates = [s.unemployment_rate for s in stats if s.unemployment_rate]
        informal_rates = [s.informal_rate for s in stats if s.informal_rate]
        salaries = [s.median_salary for s in stats if s.median_salary and s.median_salary > 0]
        qualities = [s.data_quality_score for s in stats if s.data_quality_score]
        
        kpis = {
            'total_employed': sum(employed) if employed else 0,
            'avg_unemployment_rate': sum(unemp_rates) / len(unemp_rates) if unemp_rates else 0,
            'avg_informal_rate': sum(informal_rates) / len(informal_rates) if informal_rates else 0,
            'avg_median_salary': sum(salaries) / len(salaries) if salaries else 0,
            'data_quality_avg': sum(qualities) / len(qualities) if qualities else 0
        }

        return {
            'kpis': kpis,
            'metadata': {
                'total_records': len(stats),
                'year_range': (min([s.year for s in stats]), max([s.year for s in stats])),
                'num_communes': len(set([s.commune_id for s in stats])),
                'num_job_categories': len(set([s.job_category_id for s in stats]))
            }
        }

    def _aggregate_by_commune(self, results):
        """Aggregate statistics by commune"""
        by_commune = {}
        
        for stat, commune_name, job_category_name in results:
            commune_id = stat.commune_id
            if commune_id not in by_commune:
                by_commune[commune_id] = {
                    'commune_id': commune_id,
                    'commune_name': commune_name,
                    'employed': [],
                    'unemployment_rates': [],
                    'informal_rates': [],
                    'salaries': [],
                    'quality_scores': []
                }
            
            if stat.total_employed:
                by_commune[commune_id]['employed'].append(stat.total_employed)
            if stat.unemployment_rate:
                by_commune[commune_id]['unemployment_rates'].append(stat.unemployment_rate)
            if stat.informal_rate:
                by_commune[commune_id]['informal_rates'].append(stat.informal_rate)
            if stat.median_salary and stat.median_salary > 0:
                by_commune[commune_id]['salaries'].append(stat.median_salary)
            if stat.data_quality_score:
                by_commune[commune_id]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for commune_id, data in by_commune.items():
            agg = {
                'commune_id': data['commune_id'],
                'commune_name': data['commune_name'],
                'total_employed': sum(data['employed']) if data['employed'] else 0,
                'avg_unemployment_rate': sum(data['unemployment_rates']) / len(data['unemployment_rates']) if data['unemployment_rates'] else 0,
                'avg_informal_rate': sum(data['informal_rates']) / len(data['informal_rates']) if data['informal_rates'] else 0,
                'avg_median_salary': sum(data['salaries']) / len(data['salaries']) if data['salaries'] else 0,
                'data_quality': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            }
            aggregated.append(agg)

        # Sort by employed count
        aggregated.sort(key=lambda x: x['total_employed'], reverse=True)
        
        return {
            'data': aggregated,
            'metadata': {
                'group_by': 'commune',
                'total_communes': len(aggregated),
                'records': len(results)
            }
        }

    def _aggregate_by_job_category(self, results):
        """Aggregate statistics by job category"""
        by_category = {}
        
        for stat, commune_name, job_category_name in results:
            job_cat_id = stat.job_category_id
            if job_cat_id not in by_category:
                by_category[job_cat_id] = {
                    'job_category_id': job_cat_id,
                    'job_category_name': job_category_name,
                    'employed': [],
                    'unemployment_rates': [],
                    'informal_rates': [],
                    'salaries': [],
                    'quality_scores': []
                }
            
            if stat.total_employed:
                by_category[job_cat_id]['employed'].append(stat.total_employed)
            if stat.unemployment_rate:
                by_category[job_cat_id]['unemployment_rates'].append(stat.unemployment_rate)
            if stat.informal_rate:
                by_category[job_cat_id]['informal_rates'].append(stat.informal_rate)
            if stat.median_salary and stat.median_salary > 0:
                by_category[job_cat_id]['salaries'].append(stat.median_salary)
            if stat.data_quality_score:
                by_category[job_cat_id]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for job_cat_id, data in by_category.items():
            agg = {
                'job_category_id': data['job_category_id'],
                'job_category_name': data['job_category_name'],
                'total_employed': sum(data['employed']) if data['employed'] else 0,
                'avg_unemployment_rate': sum(data['unemployment_rates']) / len(data['unemployment_rates']) if data['unemployment_rates'] else 0,
                'avg_informal_rate': sum(data['informal_rates']) / len(data['informal_rates']) if data['informal_rates'] else 0,
                'avg_median_salary': sum(data['salaries']) / len(data['salaries']) if data['salaries'] else 0,
                'data_quality': sum(data['quality_scores']) / len(data['quality_scores']) if data['quality_scores'] else 0
            }
            aggregated.append(agg)

        aggregated.sort(key=lambda x: x['total_employed'], reverse=True)
        
        return {
            'data': aggregated,
            'metadata': {
                'group_by': 'job_category',
                'total_categories': len(aggregated),
                'records': len(results)
            }
        }

    def _aggregate_by_year(self, results):
        """Aggregate statistics by year"""
        by_year = {}
        
        for stat, commune_name, job_category_name in results:
            year = stat.year
            if year not in by_year:
                by_year[year] = {
                    'year': year,
                    'employed': [],
                    'unemployment_rates': [],
                    'informal_rates': [],
                    'salaries': [],
                    'quality_scores': []
                }
            
            if stat.total_employed:
                by_year[year]['employed'].append(stat.total_employed)
            if stat.unemployment_rate:
                by_year[year]['unemployment_rates'].append(stat.unemployment_rate)
            if stat.informal_rate:
                by_year[year]['informal_rates'].append(stat.informal_rate)
            if stat.median_salary and stat.median_salary > 0:
                by_year[year]['salaries'].append(stat.median_salary)
            if stat.data_quality_score:
                by_year[year]['quality_scores'].append(stat.data_quality_score)

        # Calculate aggregates
        aggregated = []
        for year in sorted(by_year.keys()):
            data = by_year[year]
            agg = {
                'year': data['year'],
                'total_employed': sum(data['employed']) if data['employed'] else 0,
                'avg_unemployment_rate': sum(data['unemployment_rates']) / len(data['unemployment_rates']) if data['unemployment_rates'] else 0,
                'avg_informal_rate': sum(data['informal_rates']) / len(data['informal_rates']) if data['informal_rates'] else 0,
                'avg_median_salary': sum(data['salaries']) / len(data['salaries']) if data['salaries'] else 0,
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
