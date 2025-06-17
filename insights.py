"""
AI-powered insights generation service
Uses LLM to generate structured, actionable pricing recommendations and insights
"""

import json
import requests
from typing import Dict, List, Optional
from src.models.vehicle import Vehicle, VehicleScore
from src.services.scoring import ScoringService
from src.services.matching import VehicleMatchingEngine, MarketAnalyzer
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsightsGenerator:
    """Generate AI-powered insights and recommendations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize insights generator
        Note: For demo purposes, we'll use a mock LLM service
        In production, you would integrate with OpenAI, Claude, or similar
        """
        self.api_key = api_key
        self.scoring_service = ScoringService()
        self.matching_engine = VehicleMatchingEngine()
        self.market_analyzer = MarketAnalyzer()
    
    def generate_vehicle_insights(self, vehicle: Vehicle, include_comparisons: bool = True) -> Dict:
        """
        Generate comprehensive insights for a specific vehicle
        """
        
        logger.info(f"Generating insights for vehicle: {vehicle.vin}")
        
        # Get scoring data
        score_data = self.scoring_service.get_vehicle_score(vehicle)
        if not score_data:
            # Calculate score if not exists
            score_analysis = self.scoring_service.calculate_and_store_score(vehicle)
            score_data = score_analysis
        
        # Get market matches if requested
        matches = []
        if include_comparisons:
            matches = self.matching_engine.get_stored_matches(vehicle, limit=5)
            if not matches:
                # Find matches if none stored
                match_result = self.matching_engine.find_and_store_matches(
                    vehicle, min_similarity=0.3, max_matches=5, exclude_same_dealer=False
                )
                matches = self.matching_engine.get_stored_matches(vehicle, limit=5)
        
        # Prepare context for LLM
        context = self._prepare_context(vehicle, score_data, matches)
        
        # Generate insights using LLM (mock implementation)
        insights = self._generate_llm_insights(context)
        
        return {
            'vehicle_id': vehicle.id,
            'vin': vehicle.vin,
            'insights': insights,
            'context_data': {
                'score_summary': self._extract_score_summary(score_data),
                'market_comparisons': len(matches),
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    def _prepare_context(self, vehicle: Vehicle, score_data: Dict, matches: List[Dict]) -> Dict:
        """Prepare structured context for LLM"""
        
        # Vehicle summary
        vehicle_summary = {
            'year': vehicle.year,
            'make': vehicle.make,
            'model': vehicle.model,
            'trim': vehicle.trim,
            'condition': vehicle.condition,
            'mileage': vehicle.mileage,
            'price': vehicle.price,
            'dealer': vehicle.dealer_name
        }
        
        # Score summary
        if isinstance(score_data, dict) and 'component_scores' in score_data:
            score_summary = {
                'overall_score': score_data.get('overall_score', 0),
                'price_score': score_data['component_scores'].get('price_score', 0),
                'age_score': score_data['component_scores'].get('age_score', 0),
                'scarcity_score': score_data['component_scores'].get('scarcity_score', 0),
                'market_position': score_data.get('market_position', 'unknown')
            }
        else:
            score_summary = {
                'overall_score': getattr(score_data, 'overall_score', 0) if score_data else 0,
                'price_score': getattr(score_data, 'price_score', 0) if score_data else 0,
                'age_score': getattr(score_data, 'age_score', 0) if score_data else 0,
                'scarcity_score': getattr(score_data, 'scarcity_score', 0) if score_data else 0,
                'market_position': getattr(score_data, 'market_position', 'unknown') if score_data else 'unknown'
            }
        
        # Market comparisons
        comparable_vehicles = []
        for match in matches[:3]:  # Top 3 matches
            if 'vehicle' in match:
                comp_vehicle = match['vehicle']
                comparable_vehicles.append({
                    'year': comp_vehicle.get('year'),
                    'make': comp_vehicle.get('make'),
                    'model': comp_vehicle.get('model'),
                    'trim': comp_vehicle.get('trim'),
                    'condition': comp_vehicle.get('condition'),
                    'mileage': comp_vehicle.get('mileage'),
                    'price': comp_vehicle.get('price'),
                    'similarity_score': match.get('similarity_score', 0)
                })
        
        return {
            'target_vehicle': vehicle_summary,
            'scoring_analysis': score_summary,
            'comparable_vehicles': comparable_vehicles,
            'market_context': {
                'total_comparables': len(matches),
                'analysis_date': datetime.utcnow().strftime('%Y-%m-%d')
            }
        }
    
    def _generate_llm_insights(self, context: Dict) -> Dict:
        """
        Generate insights using LLM (mock implementation)
        In production, this would call OpenAI, Claude, or similar API
        """
        
        # Mock LLM response based on context analysis
        vehicle = context['target_vehicle']
        scores = context['scoring_analysis']
        comparables = context['comparable_vehicles']
        
        # Generate structured insights
        insights = {
            'executive_summary': self._generate_executive_summary(vehicle, scores),
            'pricing_analysis': self._generate_pricing_analysis(vehicle, scores, comparables),
            'market_positioning': self._generate_market_positioning(scores, comparables),
            'recommendations': self._generate_recommendations(vehicle, scores, comparables),
            'risk_factors': self._generate_risk_factors(vehicle, scores),
            'opportunities': self._generate_opportunities(vehicle, scores, comparables)
        }
        
        return insights
    
    def _generate_executive_summary(self, vehicle: Dict, scores: Dict) -> str:
        """Generate executive summary"""
        
        year = vehicle.get('year', 'Unknown')
        make = vehicle.get('make', 'Unknown')
        model = vehicle.get('model', 'Unknown')
        condition = vehicle.get('condition', 'Unknown')
        price = vehicle.get('price', 0)
        overall_score = scores.get('overall_score', 0)
        market_position = scores.get('market_position', 'unknown')
        
        if overall_score >= 70:
            performance = "strong competitive position"
        elif overall_score >= 50:
            performance = "moderate competitive position"
        else:
            performance = "challenging competitive position"
        
        summary = f"The {year} {make} {model} ({condition}) priced at ${price:,.0f} currently holds a {performance} " \
                 f"with an overall competitiveness score of {overall_score:.1f}/100. The vehicle is positioned as " \
                 f"'{market_position.replace('_', ' ')}' in the current market landscape."
        
        return summary
    
    def _generate_pricing_analysis(self, vehicle: Dict, scores: Dict, comparables: List[Dict]) -> Dict:
        """Generate detailed pricing analysis"""
        
        price = vehicle.get('price', 0)
        price_score = scores.get('price_score', 0)
        
        analysis = {
            'current_price': price,
            'price_competitiveness_score': price_score,
            'market_comparison': 'Limited comparable data available' if not comparables else f'Compared against {len(comparables)} similar vehicles',
            'pricing_insights': []
        }
        
        if price_score == 0:
            analysis['pricing_insights'].append("Insufficient market data for comprehensive price comparison")
        elif price_score >= 80:
            analysis['pricing_insights'].append("Vehicle is competitively priced compared to market")
        elif price_score >= 50:
            analysis['pricing_insights'].append("Vehicle pricing is within acceptable market range")
        else:
            analysis['pricing_insights'].append("Vehicle may be overpriced relative to market conditions")
        
        # Add comparable vehicle analysis
        if comparables:
            prices = [comp.get('price', 0) for comp in comparables if comp.get('price')]
            if prices:
                avg_comp_price = sum(prices) / len(prices)
                price_diff = price - avg_comp_price
                price_diff_pct = (price_diff / avg_comp_price) * 100 if avg_comp_price > 0 else 0
                
                analysis['comparable_avg_price'] = avg_comp_price
                analysis['price_difference'] = price_diff
                analysis['price_difference_pct'] = price_diff_pct
                
                if abs(price_diff_pct) <= 5:
                    analysis['pricing_insights'].append("Price is closely aligned with comparable vehicles")
                elif price_diff_pct > 5:
                    analysis['pricing_insights'].append(f"Price is {price_diff_pct:.1f}% above comparable vehicles")
                else:
                    analysis['pricing_insights'].append(f"Price is {abs(price_diff_pct):.1f}% below comparable vehicles")
        
        return analysis
    
    def _generate_market_positioning(self, scores: Dict, comparables: List[Dict]) -> Dict:
        """Generate market positioning analysis"""
        
        overall_score = scores.get('overall_score', 0)
        age_score = scores.get('age_score', 0)
        scarcity_score = scores.get('scarcity_score', 0)
        market_position = scores.get('market_position', 'unknown')
        
        positioning = {
            'market_position': market_position.replace('_', ' ').title(),
            'competitive_strengths': [],
            'competitive_weaknesses': [],
            'market_dynamics': []
        }
        
        # Analyze strengths
        if age_score >= 70:
            positioning['competitive_strengths'].append("Vehicle age provides strong market appeal")
        if scarcity_score >= 70:
            positioning['competitive_strengths'].append("Limited market availability supports premium positioning")
        if overall_score >= 60:
            positioning['competitive_strengths'].append("Strong overall competitive position")
        
        # Analyze weaknesses
        if age_score < 40:
            positioning['competitive_weaknesses'].append("Vehicle age may limit market appeal")
        if scarcity_score < 30:
            positioning['competitive_weaknesses'].append("High market availability creates pricing pressure")
        if overall_score < 40:
            positioning['competitive_weaknesses'].append("Overall competitive position needs improvement")
        
        # Market dynamics
        if len(comparables) == 0:
            positioning['market_dynamics'].append("Limited comparable inventory may indicate niche market opportunity")
        elif len(comparables) >= 5:
            positioning['market_dynamics'].append("Abundant comparable inventory suggests competitive market")
        else:
            positioning['market_dynamics'].append("Moderate comparable inventory indicates balanced market conditions")
        
        return positioning
    
    def _generate_recommendations(self, vehicle: Dict, scores: Dict, comparables: List[Dict]) -> Dict:
        """Generate actionable recommendations"""
        
        overall_score = scores.get('overall_score', 0)
        price_score = scores.get('price_score', 0)
        market_position = scores.get('market_position', 'unknown')
        
        recommendations = {
            'primary_actions': [],
            'secondary_actions': [],
            'timeline': 'immediate',
            'expected_impact': 'medium'
        }
        
        # Primary recommendations based on overall score
        if overall_score < 40:
            recommendations['primary_actions'].append("Conduct comprehensive pricing review")
            recommendations['primary_actions'].append("Consider price reduction to improve competitiveness")
            recommendations['timeline'] = 'immediate'
            recommendations['expected_impact'] = 'high'
        elif overall_score < 60:
            recommendations['primary_actions'].append("Monitor market conditions closely")
            recommendations['primary_actions'].append("Evaluate pricing strategy against competitors")
            recommendations['timeline'] = 'within 1-2 weeks'
            recommendations['expected_impact'] = 'medium'
        else:
            recommendations['primary_actions'].append("Maintain current pricing strategy")
            recommendations['primary_actions'].append("Continue market monitoring")
            recommendations['timeline'] = 'ongoing'
            recommendations['expected_impact'] = 'low'
        
        # Secondary recommendations
        if price_score == 0:
            recommendations['secondary_actions'].append("Gather more market data for better pricing insights")
        
        if len(comparables) < 3:
            recommendations['secondary_actions'].append("Expand comparable vehicle analysis")
        
        recommendations['secondary_actions'].append("Track vehicle performance metrics weekly")
        recommendations['secondary_actions'].append("Review and update pricing based on market changes")
        
        return recommendations
    
    def _generate_risk_factors(self, vehicle: Dict, scores: Dict) -> List[str]:
        """Generate risk factor analysis"""
        
        risks = []
        
        age_score = scores.get('age_score', 0)
        price_score = scores.get('price_score', 0)
        overall_score = scores.get('overall_score', 0)
        
        if age_score < 30:
            risks.append("Vehicle age may lead to accelerated depreciation")
        
        if price_score < 30 and price_score > 0:
            risks.append("Current pricing may be above market tolerance")
        
        if overall_score < 30:
            risks.append("Poor competitive position may result in extended time on lot")
        
        if price_score == 0:
            risks.append("Lack of market data creates pricing uncertainty")
        
        # Default risk if none identified
        if not risks:
            risks.append("Standard market volatility and seasonal demand fluctuations")
        
        return risks
    
    def _generate_opportunities(self, vehicle: Dict, scores: Dict, comparables: List[Dict]) -> List[str]:
        """Generate opportunity analysis"""
        
        opportunities = []
        
        scarcity_score = scores.get('scarcity_score', 0)
        age_score = scores.get('age_score', 0)
        overall_score = scores.get('overall_score', 0)
        
        if scarcity_score >= 70:
            opportunities.append("Limited market availability supports premium pricing opportunity")
        
        if age_score >= 70:
            opportunities.append("Vehicle age profile appeals to quality-conscious buyers")
        
        if overall_score >= 60:
            opportunities.append("Strong competitive position enables confident pricing strategy")
        
        if len(comparables) == 0:
            opportunities.append("Unique market position may attract specific buyer segments")
        
        # Market-based opportunities
        opportunities.append("Seasonal demand patterns may create pricing opportunities")
        opportunities.append("Targeted marketing can highlight vehicle's competitive advantages")
        
        return opportunities
    
    def _extract_score_summary(self, score_data) -> Dict:
        """Extract key score information for context"""
        
        if isinstance(score_data, dict):
            return {
                'overall_score': score_data.get('overall_score', 0),
                'market_position': score_data.get('market_position', 'unknown')
            }
        else:
            return {
                'overall_score': getattr(score_data, 'overall_score', 0) if score_data else 0,
                'market_position': getattr(score_data, 'market_position', 'unknown') if score_data else 'unknown'
            }
    
    def generate_market_insights(self, filters: Dict = None) -> Dict:
        """Generate market-level insights across multiple vehicles"""
        
        logger.info("Generating market-level insights")
        
        # Get market analytics
        analytics = self.scoring_service.get_scoring_analytics()
        
        # Generate market insights
        market_insights = {
            'market_overview': self._generate_market_overview(analytics),
            'pricing_trends': self._generate_pricing_trends(analytics),
            'inventory_analysis': self._generate_inventory_analysis(analytics),
            'strategic_recommendations': self._generate_strategic_recommendations(analytics),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return market_insights
    
    def _generate_market_overview(self, analytics: Dict) -> str:
        """Generate market overview summary"""
        
        total_vehicles = analytics.get('total_vehicles', 0)
        scored_vehicles = analytics.get('scored_vehicles', 0)
        avg_score = analytics.get('score_distribution', {}).get('avg_score', 0)
        
        overview = f"Market analysis covers {total_vehicles} vehicles with {scored_vehicles} scored for competitiveness. " \
                  f"The average market competitiveness score is {avg_score:.1f}/100, indicating "
        
        if avg_score >= 70:
            overview += "a highly competitive market environment."
        elif avg_score >= 50:
            overview += "a moderately competitive market with mixed positioning."
        else:
            overview += "a challenging market with significant pricing pressures."
        
        return overview
    
    def _generate_pricing_trends(self, analytics: Dict) -> Dict:
        """Generate pricing trend analysis"""
        
        return {
            'trend_direction': 'stable',  # Would analyze historical data in production
            'price_volatility': 'moderate',
            'market_sentiment': 'neutral',
            'key_insights': [
                "Market pricing remains within historical ranges",
                "Competitive pressure varies by vehicle segment",
                "Seasonal factors may influence pricing dynamics"
            ]
        }
    
    def _generate_inventory_analysis(self, analytics: Dict) -> Dict:
        """Generate inventory analysis"""
        
        positions = analytics.get('market_positions', [])
        actions = analytics.get('recommended_actions', [])
        
        analysis = {
            'inventory_health': 'mixed',
            'attention_required': 0,
            'well_positioned': 0,
            'key_findings': []
        }
        
        # Analyze market positions
        for position in positions:
            if position['position'] in ['poor', 'below_average']:
                analysis['attention_required'] += position['count']
            elif position['position'] in ['excellent', 'competitive']:
                analysis['well_positioned'] += position['count']
        
        # Generate findings
        if analysis['attention_required'] > analysis['well_positioned']:
            analysis['inventory_health'] = 'needs_attention'
            analysis['key_findings'].append("Significant portion of inventory requires pricing attention")
        elif analysis['well_positioned'] > analysis['attention_required']:
            analysis['inventory_health'] = 'strong'
            analysis['key_findings'].append("Majority of inventory is well-positioned competitively")
        
        analysis['key_findings'].append("Regular monitoring recommended for all inventory")
        
        return analysis
    
    def _generate_strategic_recommendations(self, analytics: Dict) -> List[str]:
        """Generate strategic recommendations"""
        
        recommendations = [
            "Implement regular competitive pricing reviews",
            "Establish automated monitoring for market changes",
            "Develop segment-specific pricing strategies",
            "Create alerts for vehicles requiring immediate attention"
        ]
        
        coverage_pct = analytics.get('coverage_pct', 0)
        if coverage_pct < 50:
            recommendations.insert(0, "Expand scoring coverage to include all inventory")
        
        return recommendations

