"""
Multi-source data quality scoring utility
Implements the quality scoring algorithm based on number and concordance of sources
"""
import statistics
from typing import List, Dict, Any, Optional


class MultiSourceQualityScorer:
    """
    Calculates data quality scores based on multi-source validation

    Scoring Rules (from CLAUDE.md):
    - 1 source: Quality = 60% max
    - 2 sources concordantes: Quality = 80%
    - 3+ sources concordantes: Quality = 95%+
    - Sources conflictuelles: Flag pour révision manuelle
    """

    # Base scores
    BASE_SCORE_SINGLE = 0.60
    BASE_SCORE_DUAL = 0.80
    BASE_SCORE_MULTI = 0.95

    # Thresholds
    CONCORDANCE_THRESHOLD = 0.10  # 10% deviation threshold for concordance
    HIGH_DEVIATION_THRESHOLD = 0.25  # 25% deviation triggers manual review flag

    @classmethod
    def calculate_quality_score(
        cls,
        values: List[float],
        confidence_scores: Optional[List[float]] = None,
        source_weights: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate aggregated quality score from multiple source values

        Args:
            values: List of values from different sources
            confidence_scores: Optional confidence score for each source (0-1)
            source_weights: Optional weight for each source (0-1)

        Returns:
            Dictionary with:
                - final_value: Weighted average of values
                - quality_score: Overall quality score (0-1)
                - num_sources: Number of sources
                - is_concordant: Whether sources agree
                - needs_review: Whether manual review is needed
                - deviations: List of deviations from final value
                - std_deviation: Standard deviation of values
        """
        if not values:
            return {
                'final_value': None,
                'quality_score': 0.0,
                'num_sources': 0,
                'is_concordant': False,
                'needs_review': True,
                'deviations': [],
                'std_deviation': None
            }

        num_sources = len(values)

        # Default weights and confidences if not provided
        if source_weights is None:
            source_weights = [1.0] * num_sources
        if confidence_scores is None:
            confidence_scores = [1.0] * num_sources

        # Calculate weighted average
        total_weight = sum(w * c for w, c in zip(source_weights, confidence_scores))
        if total_weight == 0:
            final_value = statistics.mean(values)
        else:
            final_value = sum(
                v * w * c for v, w, c in zip(values, source_weights, confidence_scores)
            ) / total_weight

        # Calculate deviations from final value
        deviations = [
            abs((v - final_value) / final_value) if final_value != 0 else 0
            for v in values
        ]

        # Calculate standard deviation
        std_dev = statistics.stdev(values) if num_sources > 1 else 0.0
        std_dev_percent = (std_dev / final_value) if final_value != 0 else 0.0

        # Check concordance
        is_concordant = all(d <= cls.CONCORDANCE_THRESHOLD for d in deviations)

        # Flag for manual review if high deviation
        needs_review = any(d > cls.HIGH_DEVIATION_THRESHOLD for d in deviations)

        # Calculate base quality score
        if num_sources == 1:
            base_score = cls.BASE_SCORE_SINGLE
        elif num_sources == 2:
            base_score = cls.BASE_SCORE_DUAL
        else:
            base_score = cls.BASE_SCORE_MULTI

        # Adjust score based on concordance
        if is_concordant:
            quality_score = base_score
        else:
            # Reduce score based on deviation
            max_deviation = max(deviations)
            penalty = min(max_deviation, 0.3)  # Max 30% penalty
            quality_score = max(base_score - penalty, 0.3)  # Min 30%

        # Bonus for more sources if concordant
        if num_sources >= 3 and is_concordant:
            quality_score = min(quality_score + (num_sources - 3) * 0.01, 1.0)

        # Apply confidence multiplier
        avg_confidence = statistics.mean(confidence_scores)
        quality_score *= avg_confidence

        return {
            'final_value': final_value,
            'quality_score': quality_score,
            'num_sources': num_sources,
            'is_concordant': is_concordant,
            'needs_review': needs_review,
            'deviations': deviations,
            'std_deviation': std_dev,
            'std_deviation_percent': std_dev_percent,
            'max_deviation': max(deviations) if deviations else 0.0
        }

    @classmethod
    def assign_source_contributions(
        cls,
        stat_id: int,
        source_values: List[Dict[str, Any]],
        stat_type: str = 'agriculture'
    ) -> List[Dict[str, Any]]:
        """
        Prepare source contribution records for database insertion

        Args:
            stat_id: ID of the statistic record
            source_values: List of dicts with 'source_id', 'value', 'confidence', 'weight'
            stat_type: Type of statistic ('agriculture', 'realestate', 'employment', 'business')

        Returns:
            List of contribution records ready for insertion
        """
        if not source_values:
            return []

        # Extract values and metadata
        values = [sv['value'] for sv in source_values]
        confidences = [sv.get('confidence', 1.0) for sv in source_values]
        weights = [sv.get('weight', 1.0) for sv in source_values]

        # Calculate quality metrics
        quality_metrics = cls.calculate_quality_score(values, confidences, weights)
        final_value = quality_metrics['final_value']

        # Prepare contribution records
        contributions = []
        for i, source_val in enumerate(source_values):
            deviation = abs((source_val['value'] - final_value) / final_value) \
                if final_value != 0 else 0.0

            contribution = {
                f'{stat_type}_stat_id': stat_id,
                'data_source_id': source_val['source_id'],
                'contribution_weight': weights[i],
                'confidence_score': confidences[i],
                'is_primary': i == 0,  # First source is primary
                'source_value': source_val['value'],
                'deviation_from_final': deviation
            }
            contributions.append(contribution)

        return contributions

    @classmethod
    def get_quality_tier(cls, quality_score: float) -> str:
        """
        Get quality tier label from score

        Args:
            quality_score: Score from 0-1

        Returns:
            Quality tier: 'excellent', 'good', 'fair', 'poor'
        """
        if quality_score >= 0.90:
            return 'excellent'
        elif quality_score >= 0.75:
            return 'good'
        elif quality_score >= 0.60:
            return 'fair'
        else:
            return 'poor'

    @classmethod
    def validate_multi_source_data(
        cls,
        data_points: List[Dict[str, Any]],
        value_field: str = 'value'
    ) -> Dict[str, Any]:
        """
        Validate and aggregate multiple data points from different sources

        Args:
            data_points: List of data point dicts from different sources
            value_field: Name of the field containing the value

        Returns:
            Aggregated result with quality metrics
        """
        if not data_points:
            return {
                'aggregated_value': None,
                'quality_score': 0.0,
                'quality_tier': 'poor',
                'num_sources': 0,
                'recommendation': 'No data available'
            }

        values = [dp[value_field] for dp in data_points if dp.get(value_field) is not None]
        confidences = [dp.get('confidence', 1.0) for dp in data_points]

        if not values:
            return {
                'aggregated_value': None,
                'quality_score': 0.0,
                'quality_tier': 'poor',
                'num_sources': 0,
                'recommendation': 'All data points have null values'
            }

        quality_metrics = cls.calculate_quality_score(values, confidences)

        # Generate recommendation
        if quality_metrics['needs_review']:
            recommendation = 'Manual review recommended - high deviation between sources'
        elif quality_metrics['num_sources'] == 1:
            recommendation = 'Single source - consider adding more sources for validation'
        elif quality_metrics['is_concordant']:
            recommendation = 'Data validated by multiple concordant sources'
        else:
            recommendation = 'Multiple sources with some variance - acceptable quality'

        return {
            'aggregated_value': quality_metrics['final_value'],
            'quality_score': quality_metrics['quality_score'],
            'quality_tier': cls.get_quality_tier(quality_metrics['quality_score']),
            'num_sources': quality_metrics['num_sources'],
            'is_concordant': quality_metrics['is_concordant'],
            'needs_review': quality_metrics['needs_review'],
            'std_deviation_percent': quality_metrics['std_deviation_percent'],
            'recommendation': recommendation
        }
