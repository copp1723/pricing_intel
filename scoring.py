"""
Pricing scoring and analytics service
Calculates competitive scores based on market position, age, and scarcity factors
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from src.models.vehicle import db, Vehicle, VehicleScore, VehicleMatch
from src.services.matching import VehicleMatchingEngine, MarketAnalyzer
from sqlalchemy import and_, or_, func
from datetime import datetime, date
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PricingScoreCalculator:
    """Calculate pricing scores for vehicles based on multiple factors"""
    
    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        'price_competitiveness': 0.40,  # How competitive the price is vs market
        'age_factor': 0.30,            # Vehicle age impact
        'scarcity_factor': 0.30        # Market scarcity/availability
    }
    
    def __init__(self):
        self.matching_engine = VehicleMatchingEngine()
        self.market_analyzer = MarketAnalyzer()
    
    def calculate_price_score(self, vehicle: Vehicle, market_data: Dict) -> Tuple[float, Dict]:
        """
        Calculate price competitiveness score (0-100)
        Higher score = more competitive pricing
        """
        
        if not vehicle.price or not market_data.get('market_stats'):
            return 0.0, {'reason': 'no_price_data'}
        
        market_stats = market_data['market_stats']
        target_price = vehicle.price
        
        # No comparable vehicles
        if market_stats['sample_size'] == 0:
            return 50.0, {'reason': 'no_comparables', 'default_score': True}
        
        avg_price = market_stats['avg_price']
        min_price = market_stats['min_price']
        max_price = market_stats['max_price']
        
        # Calculate percentile rank (lower price = higher score)
        percentile = market_data.get('percentile_rank', 50)
        
        # Convert percentile to score (invert so lower price = higher score)
        if percentile <= 10:
            score = 95.0  # Significantly underpriced
        elif percentile <= 25:
            score = 85.0  # Underpriced
        elif percentile <= 50:
            score = 75.0  # Below average
        elif percentile <= 75:
            score = 50.0  # Above average
        elif percentile <= 90:
            score = 25.0  # Overpriced
        else:
            score = 10.0  # Significantly overpriced
        
        # Calculate price difference from market average
        price_diff_pct = ((target_price - avg_price) / avg_price) * 100
        
        details = {
            'target_price': target_price,
            'market_avg': avg_price,
            'percentile_rank': percentile,
            'price_diff_pct': price_diff_pct,
            'market_position': market_data.get('market_position', 'unknown'),
            'sample_size': market_stats['sample_size']
        }
        
        return score, details
    
    def calculate_age_score(self, vehicle: Vehicle) -> Tuple[float, Dict]:
        """
        Calculate age factor score (0-100)
        Higher score = newer/more desirable age
        """
        
        if not vehicle.year:
            return 50.0, {'reason': 'no_year_data', 'default_score': True}
        
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        
        # Score based on age
        if vehicle_age <= 0:  # Future model year
            score = 100.0
        elif vehicle_age == 1:  # 1 year old
            score = 90.0
        elif vehicle_age == 2:  # 2 years old
            score = 80.0
        elif vehicle_age == 3:  # 3 years old
            score = 70.0
        elif vehicle_age <= 5:  # 4-5 years old
            score = 60.0
        elif vehicle_age <= 7:  # 6-7 years old
            score = 45.0
        elif vehicle_age <= 10:  # 8-10 years old
            score = 30.0
        elif vehicle_age <= 15:  # 11-15 years old
            score = 15.0
        else:  # 15+ years old
            score = 5.0
        
        # Adjust for condition
        condition_multiplier = 1.0
        if vehicle.condition == 'New':
            condition_multiplier = 1.0
        elif vehicle.condition == 'Certified':
            condition_multiplier = 0.95
        elif vehicle.condition == 'Used':
            condition_multiplier = 0.85
        
        final_score = score * condition_multiplier
        
        details = {
            'vehicle_year': vehicle.year,
            'current_year': current_year,
            'age_years': vehicle_age,
            'condition': vehicle.condition,
            'base_score': score,
            'condition_multiplier': condition_multiplier,
            'final_score': final_score
        }
        
        return final_score, details
    
    def calculate_scarcity_score(self, vehicle: Vehicle) -> Tuple[float, Dict]:
        """
        Calculate market scarcity score (0-100)
        Higher score = more scarce/unique in market
        """
        
        # Count similar vehicles in market
        similar_vehicles = Vehicle.query.filter(
            and_(
                Vehicle.make == vehicle.make,
                Vehicle.model == vehicle.model,
                Vehicle.year == vehicle.year,
                Vehicle.id != vehicle.id
            )
        ).count()
        
        # Count exact matches (same trim)
        exact_matches = Vehicle.query.filter(
            and_(
                Vehicle.make == vehicle.make,
                Vehicle.model == vehicle.model,
                Vehicle.year == vehicle.year,
                Vehicle.trim == vehicle.trim,
                Vehicle.id != vehicle.id
            )
        ).count()
        
        # Count total vehicles of same make/model (any year)
        total_make_model = Vehicle.query.filter(
            and_(
                Vehicle.make == vehicle.make,
                Vehicle.model == vehicle.model,
                Vehicle.id != vehicle.id
            )
        ).count()
        
        # Calculate scarcity score
        if exact_matches == 0:
            score = 95.0  # Unique trim
        elif exact_matches <= 2:
            score = 85.0  # Very rare
        elif exact_matches <= 5:
            score = 70.0  # Rare
        elif exact_matches <= 10:
            score = 55.0  # Uncommon
        elif exact_matches <= 20:
            score = 40.0  # Common
        else:
            score = 20.0  # Very common
        
        # Adjust based on similar year vehicles
        if similar_vehicles <= 5:
            score += 10  # Bonus for rare year
        elif similar_vehicles >= 20:
            score -= 10  # Penalty for common year
        
        # Ensure score stays in bounds
        score = max(0.0, min(100.0, score))
        
        details = {
            'exact_matches': exact_matches,
            'similar_year_vehicles': similar_vehicles,
            'total_make_model': total_make_model,
            'scarcity_level': self._get_scarcity_level(score)
        }
        
        return score, details
    
    def _get_scarcity_level(self, score: float) -> str:
        """Convert scarcity score to descriptive level"""
        if score >= 90:
            return 'unique'
        elif score >= 70:
            return 'rare'
        elif score >= 50:
            return 'uncommon'
        elif score >= 30:
            return 'common'
        else:
            return 'very_common'
    
    def calculate_overall_score(self, vehicle: Vehicle) -> Dict:
        """
        Calculate overall pricing score for a vehicle
        Returns comprehensive scoring analysis
        """
        
        logger.info(f"Calculating overall score for vehicle: {vehicle.vin}")
        
        # Get market analysis
        market_data = self.market_analyzer.analyze_vehicle_market_position(vehicle)
        
        # Calculate component scores
        price_score, price_details = self.calculate_price_score(vehicle, market_data)
        age_score, age_details = self.calculate_age_score(vehicle)
        scarcity_score, scarcity_details = self.calculate_scarcity_score(vehicle)
        
        # Calculate weighted overall score
        overall_score = (
            self.WEIGHTS['price_competitiveness'] * price_score +
            self.WEIGHTS['age_factor'] * age_score +
            self.WEIGHTS['scarcity_factor'] * scarcity_score
        )
        
        # Determine market position and recommendations
        market_position = self._determine_market_position(overall_score, price_details)
        recommendations = self._generate_recommendations(
            vehicle, overall_score, price_details, age_details, scarcity_details
        )
        
        result = {
            'vehicle_id': vehicle.id,
            'vin': vehicle.vin,
            'overall_score': round(overall_score, 2),
            'component_scores': {
                'price_score': round(price_score, 2),
                'age_score': round(age_score, 2),
                'scarcity_score': round(scarcity_score, 2)
            },
            'score_weights': self.WEIGHTS,
            'market_position': market_position,
            'recommendations': recommendations,
            'details': {
                'price_analysis': price_details,
                'age_analysis': age_details,
                'scarcity_analysis': scarcity_details,
                'market_data': market_data
            },
            'calculated_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Overall score calculated: {overall_score:.2f} for {vehicle.vin}")
        return result
    
    def _determine_market_position(self, overall_score: float, price_details: Dict) -> str:
        """Determine market position based on overall score"""
        
        if overall_score >= 80:
            return 'excellent'
        elif overall_score >= 65:
            return 'competitive'
        elif overall_score >= 50:
            return 'average'
        elif overall_score >= 35:
            return 'below_average'
        else:
            return 'poor'
    
    def _generate_recommendations(self, vehicle: Vehicle, overall_score: float, 
                                price_details: Dict, age_details: Dict, 
                                scarcity_details: Dict) -> Dict:
        """Generate pricing recommendations based on analysis"""
        
        recommendations = {
            'primary_action': '',
            'price_adjustment': None,
            'reasoning': [],
            'urgency': 'medium'
        }
        
        # Price-based recommendations
        if price_details.get('market_position') == 'overpriced':
            recommendations['primary_action'] = 'reduce_price'
            if 'price_diff_pct' in price_details:
                # Suggest reducing by half the difference from market average
                suggested_reduction = abs(price_details['price_diff_pct']) * 0.5
                if vehicle.price:
                    recommendations['price_adjustment'] = -(vehicle.price * suggested_reduction / 100)
            recommendations['reasoning'].append('Vehicle is overpriced compared to market')
            recommendations['urgency'] = 'high'
            
        elif price_details.get('market_position') == 'underpriced':
            recommendations['primary_action'] = 'hold_or_increase'
            recommendations['reasoning'].append('Vehicle is competitively priced')
            recommendations['urgency'] = 'low'
            
        elif price_details.get('market_position') == 'competitive':
            recommendations['primary_action'] = 'hold'
            recommendations['reasoning'].append('Vehicle is appropriately priced for market')
            
        # Age-based adjustments
        age_score = age_details.get('final_score', 50)
        if age_score < 30:
            recommendations['reasoning'].append('Vehicle age may require price adjustment')
            if recommendations['primary_action'] == 'hold':
                recommendations['primary_action'] = 'reduce_price'
        
        # Scarcity-based adjustments
        scarcity_level = scarcity_details.get('scarcity_level', 'common')
        if scarcity_level in ['unique', 'rare']:
            recommendations['reasoning'].append('Vehicle rarity supports premium pricing')
            if recommendations['primary_action'] == 'reduce_price':
                recommendations['urgency'] = 'medium'  # Less urgent due to rarity
        
        # Overall score adjustments
        if overall_score < 40:
            recommendations['urgency'] = 'high'
            if not recommendations['reasoning']:
                recommendations['reasoning'].append('Low overall score requires attention')
        
        # Default action if none set
        if not recommendations['primary_action']:
            recommendations['primary_action'] = 'monitor'
            recommendations['reasoning'].append('Continue monitoring market conditions')
        
        return recommendations

class ScoringService:
    """Main service for vehicle scoring and analytics"""
    
    def __init__(self):
        self.calculator = PricingScoreCalculator()
    
    def calculate_and_store_score(self, vehicle: Vehicle) -> Dict:
        """Calculate score for a vehicle and store in database"""
        
        # Calculate score
        score_data = self.calculator.calculate_overall_score(vehicle)
        
        # Check if score already exists
        existing_score = VehicleScore.query.filter_by(vehicle_id=vehicle.id).first()
        
        if existing_score:
            # Update existing score
            existing_score.price_score = score_data['component_scores']['price_score']
            existing_score.age_score = score_data['component_scores']['age_score']
            existing_score.scarcity_score = score_data['component_scores']['scarcity_score']
            existing_score.overall_score = score_data['overall_score']
            existing_score.market_position = score_data['market_position']
            existing_score.percentile_rank = score_data['details']['price_analysis'].get('percentile_rank')
            existing_score.recommended_action = score_data['recommendations']['primary_action']
            existing_score.price_adjustment = score_data['recommendations']['price_adjustment']
            existing_score.calculated_at = datetime.utcnow()
            
            logger.info(f"Updated score for vehicle {vehicle.vin}")
        else:
            # Create new score
            vehicle_score = VehicleScore(
                vehicle_id=vehicle.id,
                price_score=score_data['component_scores']['price_score'],
                age_score=score_data['component_scores']['age_score'],
                scarcity_score=score_data['component_scores']['scarcity_score'],
                overall_score=score_data['overall_score'],
                market_position=score_data['market_position'],
                percentile_rank=score_data['details']['price_analysis'].get('percentile_rank'),
                recommended_action=score_data['recommendations']['primary_action'],
                price_adjustment=score_data['recommendations']['price_adjustment']
            )
            
            db.session.add(vehicle_score)
            logger.info(f"Created new score for vehicle {vehicle.vin}")
        
        db.session.commit()
        
        return score_data
    
    def get_vehicle_score(self, vehicle: Vehicle) -> Optional[Dict]:
        """Get stored score for a vehicle"""
        
        score = VehicleScore.query.filter_by(vehicle_id=vehicle.id).first()
        
        if score:
            return score.to_dict()
        
        return None
    
    def batch_calculate_scores(self, vehicle_ids: List[int] = None, 
                             batch_size: int = 50) -> Dict:
        """Calculate scores for multiple vehicles in batches"""
        
        logger.info("Starting batch score calculation")
        
        # Get vehicles to process
        if vehicle_ids:
            vehicles = Vehicle.query.filter(Vehicle.id.in_(vehicle_ids)).all()
        else:
            vehicles = Vehicle.query.all()
        
        total_vehicles = len(vehicles)
        processed = 0
        errors = 0
        
        logger.info(f"Processing {total_vehicles} vehicles in batches of {batch_size}")
        
        # Process in batches
        for i in range(0, total_vehicles, batch_size):
            batch = vehicles[i:i + batch_size]
            
            for vehicle in batch:
                try:
                    self.calculate_and_store_score(vehicle)
                    processed += 1
                    
                    if processed % 10 == 0:
                        logger.info(f"Processed {processed}/{total_vehicles} vehicles")
                        
                except Exception as e:
                    logger.error(f"Error processing vehicle {vehicle.vin}: {e}")
                    errors += 1
        
        results = {
            'total_vehicles': total_vehicles,
            'processed': processed,
            'errors': errors,
            'success_rate': (processed / total_vehicles * 100) if total_vehicles > 0 else 0,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Batch scoring complete: {results}")
        return results
    
    def get_scoring_analytics(self) -> Dict:
        """Get overall scoring analytics and statistics"""
        
        # Basic counts
        total_vehicles = Vehicle.query.count()
        scored_vehicles = VehicleScore.query.count()
        
        # Score distribution
        score_stats = db.session.query(
            func.min(VehicleScore.overall_score).label('min_score'),
            func.max(VehicleScore.overall_score).label('max_score'),
            func.avg(VehicleScore.overall_score).label('avg_score')
        ).first()
        
        # Market position distribution
        position_stats = db.session.query(
            VehicleScore.market_position,
            func.count(VehicleScore.id).label('count')
        ).group_by(VehicleScore.market_position).all()
        
        # Recommended actions distribution
        action_stats = db.session.query(
            VehicleScore.recommended_action,
            func.count(VehicleScore.id).label('count')
        ).group_by(VehicleScore.recommended_action).all()
        
        # Component score averages
        component_stats = db.session.query(
            func.avg(VehicleScore.price_score).label('avg_price_score'),
            func.avg(VehicleScore.age_score).label('avg_age_score'),
            func.avg(VehicleScore.scarcity_score).label('avg_scarcity_score')
        ).first()
        
        return {
            'total_vehicles': total_vehicles,
            'scored_vehicles': scored_vehicles,
            'unscored_vehicles': total_vehicles - scored_vehicles,
            'coverage_pct': (scored_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0,
            'score_distribution': {
                'min_score': float(score_stats.min_score) if score_stats.min_score else None,
                'max_score': float(score_stats.max_score) if score_stats.max_score else None,
                'avg_score': float(score_stats.avg_score) if score_stats.avg_score else None
            },
            'market_positions': [
                {'position': pos, 'count': count} 
                for pos, count in position_stats
            ],
            'recommended_actions': [
                {'action': action, 'count': count} 
                for action, count in action_stats
            ],
            'component_averages': {
                'avg_price_score': float(component_stats.avg_price_score) if component_stats.avg_price_score else None,
                'avg_age_score': float(component_stats.avg_age_score) if component_stats.avg_age_score else None,
                'avg_scarcity_score': float(component_stats.avg_scarcity_score) if component_stats.avg_scarcity_score else None
            }
        }

