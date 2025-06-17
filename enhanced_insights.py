"""
Enhanced AI-powered insights generation service with real LLM integration
"""

import json
import os
import requests
from typing import Dict, List, Optional, Any
from src.models.vehicle import Vehicle, VehicleScore
from src.services.scoring import ScoringService
from src.services.matching import VehicleMatchingEngine, MarketAnalyzer
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIConfig:
    """Configuration for AI/LLM integration"""
    
    def __init__(self):
        # Support multiple AI providers
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
        
        # Default to OpenAI GPT-4 if available
        self.provider = self._determine_provider()
        self.model = self._get_model_name()
        
        # Fallback to local/mock mode if no API keys
        self.use_mock = not any([self.openai_api_key, self.anthropic_api_key, self.azure_openai_key])
        
        if self.use_mock:
            logger.warning("No AI API keys found. Using mock insights generation.")
        else:
            logger.info(f"AI Provider: {self.provider}, Model: {self.model}")
    
    def _determine_provider(self) -> str:
        """Determine which AI provider to use based on available keys"""
        if self.openai_api_key:
            return 'openai'
        elif self.azure_openai_key and self.azure_openai_endpoint:
            return 'azure_openai'
        elif self.anthropic_api_key:
            return 'anthropic'
        else:
            return 'mock'
    
    def _get_model_name(self) -> str:
        """Get the appropriate model name for the provider"""
        if self.provider == 'openai':
            return 'gpt-4'
        elif self.provider == 'azure_openai':
            return 'gpt-4'  # or whatever deployment name is configured
        elif self.provider == 'anthropic':
            return 'claude-3-sonnet-20240229'
        else:
            return 'mock'

class LLMClient:
    """Client for interacting with various LLM providers"""
    
    def __init__(self, config: AIConfig):
        self.config = config
    
    def generate_insights(self, prompt: str, context: Dict) -> Dict:
        """Generate insights using the configured LLM provider"""
        
        if self.config.use_mock:
            return self._generate_mock_insights(context)
        
        try:
            if self.config.provider == 'openai':
                return self._call_openai(prompt, context)
            elif self.config.provider == 'azure_openai':
                return self._call_azure_openai(prompt, context)
            elif self.config.provider == 'anthropic':
                return self._call_anthropic(prompt, context)
            else:
                return self._generate_mock_insights(context)
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            logger.info("Falling back to mock insights generation")
            return self._generate_mock_insights(context)
    
    def _call_openai(self, prompt: str, context: Dict) -> Dict:
        """Call OpenAI API"""
        
        headers = {
            'Authorization': f'Bearer {self.config.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.config.model,
            'messages': [
                {
                    'role': 'system',
                    'content': self._get_system_prompt()
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            return self._parse_llm_response(content)
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    def _call_azure_openai(self, prompt: str, context: Dict) -> Dict:
        """Call Azure OpenAI API"""
        
        headers = {
            'api-key': self.config.azure_openai_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messages': [
                {
                    'role': 'system',
                    'content': self._get_system_prompt()
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        # Azure OpenAI endpoint format: https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions?api-version=2023-12-01-preview
        url = f"{self.config.azure_openai_endpoint}/openai/deployments/{self.config.model}/chat/completions?api-version=2023-12-01-preview"
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            return self._parse_llm_response(content)
        else:
            raise Exception(f"Azure OpenAI API error: {response.status_code} - {response.text}")
    
    def _call_anthropic(self, prompt: str, context: Dict) -> Dict:
        """Call Anthropic Claude API"""
        
        headers = {
            'x-api-key': self.config.anthropic_api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': self.config.model,
            'max_tokens': 2000,
            'temperature': 0.3,
            'messages': [
                {
                    'role': 'user',
                    'content': f"{self._get_system_prompt()}\n\n{prompt}"
                }
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['content'][0]['text']
            return self._parse_llm_response(content)
        else:
            raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM"""
        return """You are an expert automotive pricing analyst and market intelligence specialist. 
        
Your task is to analyze vehicle pricing data and generate actionable insights for automotive dealerships.

You will be provided with:
- Target vehicle details (year, make, model, trim, condition, mileage, price)
- Pricing scores and market position analysis
- Comparable vehicle data from the market
- Market context and trends

Generate a comprehensive analysis in the following JSON format:
{
    "executive_summary": "Brief 2-3 sentence overview of the vehicle's market position and pricing competitiveness",
    "pricing_analysis": {
        "current_price": number,
        "price_competitiveness_score": number,
        "market_comparison": "string describing comparison methodology",
        "comparable_avg_price": number,
        "price_difference": number,
        "price_difference_pct": number,
        "pricing_insights": ["array of specific pricing insights"]
    },
    "market_positioning": {
        "market_position": "string describing overall position",
        "competitive_strengths": ["array of competitive advantages"],
        "competitive_weaknesses": ["array of areas for improvement"],
        "market_dynamics": ["array of market trend observations"]
    },
    "recommendations": {
        "primary_actions": ["array of immediate recommended actions"],
        "secondary_actions": ["array of supporting actions"],
        "timeline": "string indicating urgency",
        "expected_impact": "high/medium/low"
    },
    "risk_factors": ["array of potential risks and challenges"],
    "opportunities": ["array of market opportunities"]
}

Focus on:
- Actionable, specific recommendations
- Data-driven insights based on the provided context
- Clear explanations of market positioning
- Realistic risk assessment
- Practical opportunities for improvement

Be concise but thorough. Avoid generic advice and focus on insights specific to the vehicle and market data provided."""
    
    def _parse_llm_response(self, content: str) -> Dict:
        """Parse LLM response and extract JSON"""
        try:
            # Try to find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON found, create structured response from text
                return self._create_structured_response_from_text(content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON response, creating structured response")
            return self._create_structured_response_from_text(content)
    
    def _create_structured_response_from_text(self, content: str) -> Dict:
        """Create structured response from unstructured text"""
        # Basic parsing to extract insights from text response
        lines = content.split('\n')
        
        return {
            "executive_summary": content[:200] + "..." if len(content) > 200 else content,
            "pricing_analysis": {
                "current_price": 0,
                "price_competitiveness_score": 0,
                "market_comparison": "Analysis based on LLM assessment",
                "pricing_insights": ["LLM-generated pricing analysis available in executive summary"]
            },
            "market_positioning": {
                "market_position": "LLM Analysis",
                "competitive_strengths": ["Detailed analysis provided by AI"],
                "competitive_weaknesses": ["See full analysis in executive summary"],
                "market_dynamics": ["Market trends analyzed by AI"]
            },
            "recommendations": {
                "primary_actions": ["Review full AI analysis for specific recommendations"],
                "secondary_actions": ["Implement AI-suggested strategies"],
                "timeline": "immediate",
                "expected_impact": "medium"
            },
            "risk_factors": ["See AI analysis for detailed risk assessment"],
            "opportunities": ["AI-identified opportunities in full analysis"]
        }
    
    def _generate_mock_insights(self, context: Dict) -> Dict:
        """Generate mock insights when no AI provider is available"""
        
        try:
            vehicle = context['target_vehicle']
            scores = context['scoring_analysis']
            comparables = context['comparable_vehicles']
            
            # Enhanced mock insights with more realistic analysis
            overall_score = scores.get('overall_score', 0)
            price = vehicle.get('price', 0)
            
            # Determine market position
            if overall_score >= 70:
                position = "Strong Market Position"
                impact = "high"
            elif overall_score >= 50:
                position = "Competitive Market Position"
                impact = "medium"
            else:
                position = "Challenging Market Position"
                impact = "high"
            
            # Calculate comparable pricing if available
            comparable_prices = [comp.get('price', 0) for comp in comparables if comp.get('price')]
            avg_comp_price = sum(comparable_prices) / len(comparable_prices) if comparable_prices else price
            price_diff = price - avg_comp_price
            price_diff_pct = (price_diff / avg_comp_price) * 100 if avg_comp_price > 0 else 0
            
            # Safely format vehicle description
            year = vehicle.get('year', 'Unknown')
            make = vehicle.get('make', 'Unknown')
            model = vehicle.get('model', 'Unknown')
            
            return {
                "executive_summary": f"The {year} {make} {model} is positioned in a {position.lower()} with a competitiveness score of {overall_score:.1f}/100. Current pricing strategy {'aligns well' if abs(price_diff_pct) <= 10 else 'may need adjustment'} with market conditions.",
                "pricing_analysis": {
                    "current_price": price,
                    "price_competitiveness_score": scores.get('price_score', 0),
                    "market_comparison": f"Analyzed against {len(comparables)} comparable vehicles",
                    "comparable_avg_price": avg_comp_price,
                    "price_difference": price_diff,
                    "price_difference_pct": price_diff_pct,
                    "pricing_insights": [
                        f"Vehicle is priced {abs(price_diff_pct):.1f}% {'above' if price_diff_pct > 0 else 'below'} market average" if comparable_prices else "Limited comparable data available",
                        "Pricing strategy should consider market positioning and competitive landscape",
                        "Regular market analysis recommended for optimal pricing"
                    ]
                },
                "market_positioning": {
                    "market_position": position,
                    "competitive_strengths": [
                        item for item in [
                            "Competitive pricing relative to market" if abs(price_diff_pct) <= 5 else None,
                            "Strong age profile" if scores.get('age_score', 0) >= 60 else None,
                            "Good market scarcity" if scores.get('scarcity_score', 0) >= 60 else None
                        ] if item is not None
                    ],
                    "competitive_weaknesses": [
                        item for item in [
                            "Pricing above market average" if price_diff_pct > 10 else None,
                            "Age factor impact" if scores.get('age_score', 0) < 40 else None,
                            "High market availability" if scores.get('scarcity_score', 0) < 30 else None
                        ] if item is not None
                    ],
                    "market_dynamics": [
                        f"Market has {'limited' if len(comparables) < 3 else 'moderate' if len(comparables) < 8 else 'abundant'} comparable inventory",
                        "Seasonal demand patterns may affect pricing strategy",
                        "Market conditions favor strategic pricing adjustments"
                    ]
                },
                "recommendations": {
                    "primary_actions": [
                        "Monitor market pricing trends weekly" if overall_score >= 60 else "Consider pricing strategy review",
                        "Evaluate competitive positioning" if overall_score < 50 else "Maintain current strategy",
                        "Implement dynamic pricing based on market feedback"
                    ],
                    "secondary_actions": [
                        "Expand comparable vehicle analysis",
                        "Track performance metrics and market response",
                        "Review pricing strategy monthly",
                        "Consider seasonal pricing adjustments"
                    ],
                    "timeline": "immediate" if overall_score < 40 else "within 2 weeks",
                    "expected_impact": impact
                },
                "risk_factors": [
                    item for item in [
                        "Market volatility may affect pricing strategy" if overall_score < 60 else None,
                        "Competitive pressure from similar vehicles" if len(comparables) > 5 else None,
                        "Seasonal demand fluctuations",
                        "Economic factors affecting automotive market"
                    ] if item is not None
                ],
                "opportunities": [
                    item for item in [
                        "Market positioning allows for premium pricing" if overall_score >= 70 else None,
                        "Limited competition creates pricing flexibility" if len(comparables) < 3 else None,
                        "Strong vehicle profile supports market confidence" if scores.get('age_score', 0) >= 60 else None,
                        "Market analysis enables strategic pricing decisions"
                    ] if item is not None
                ]
            }
        except Exception as e:
            logger.error(f"Error in mock insights generation: {str(e)}")
            # Return basic fallback insights
            return {
                "executive_summary": "Vehicle analysis completed with basic insights.",
                "pricing_analysis": {
                    "current_price": context.get('target_vehicle', {}).get('price', 0),
                    "price_competitiveness_score": 50,
                    "market_comparison": "Basic analysis performed",
                    "pricing_insights": ["Analysis completed successfully"]
                },
                "market_positioning": {
                    "market_position": "Market Analysis",
                    "competitive_strengths": ["Vehicle data processed"],
                    "competitive_weaknesses": ["Additional analysis recommended"],
                    "market_dynamics": ["Market conditions analyzed"]
                },
                "recommendations": {
                    "primary_actions": ["Review pricing strategy"],
                    "secondary_actions": ["Monitor market conditions"],
                    "timeline": "ongoing",
                    "expected_impact": "medium"
                },
                "risk_factors": ["Market volatility considerations"],
                "opportunities": ["Strategic pricing opportunities available"]
            }

class EnhancedInsightsGenerator:
    """Enhanced insights generator with real AI integration"""
    
    def __init__(self):
        self.ai_config = AIConfig()
        self.llm_client = LLMClient(self.ai_config)
        self.scoring_service = ScoringService()
        self.matching_engine = VehicleMatchingEngine()
        self.market_analyzer = MarketAnalyzer()
    
    def generate_vehicle_insights(self, vehicle: Vehicle, include_comparisons: bool = True) -> Dict:
        """Generate comprehensive AI-powered insights for a specific vehicle"""
        
        logger.info(f"Generating AI insights for vehicle: {vehicle.vin}")
        
        # Get scoring data
        score_data = self.scoring_service.get_vehicle_score(vehicle)
        if not score_data:
            score_analysis = self.scoring_service.calculate_and_store_score(vehicle)
            score_data = score_analysis
        
        # Get market matches
        matches = []
        if include_comparisons:
            matches = self.matching_engine.get_stored_matches(vehicle, limit=5)
            if not matches:
                match_result = self.matching_engine.find_and_store_matches(
                    vehicle, min_similarity=0.3, max_matches=5, exclude_same_dealer=False
                )
                matches = self.matching_engine.get_stored_matches(vehicle, limit=5)
        
        # Prepare context for AI
        context = self._prepare_ai_context(vehicle, score_data, matches)
        
        # Generate AI prompt
        prompt = self._create_ai_prompt(context)
        
        # Generate insights using AI
        insights = self.llm_client.generate_insights(prompt, context)
        
        return {
            'vehicle_id': vehicle.id,
            'vin': vehicle.vin,
            'insights': insights,
            'context_data': {
                'score_summary': self._extract_score_summary(score_data),
                'market_comparisons': len(matches),
                'generated_at': datetime.utcnow().isoformat(),
                'ai_provider': self.ai_config.provider,
                'model_used': self.ai_config.model
            }
        }
    
    def _prepare_ai_context(self, vehicle: Vehicle, score_data: Any, matches: List[Dict]) -> Dict:
        """Prepare comprehensive context for AI analysis"""
        
        # Vehicle details
        vehicle_data = {
            'vin': vehicle.vin,
            'year': vehicle.year,
            'make': vehicle.make,
            'model': vehicle.model,
            'trim': vehicle.trim or '',
            'condition': vehicle.condition or 'Unknown',
            'mileage': vehicle.mileage or 0,
            'price': vehicle.price or 0,
            'dealer': vehicle.dealer_name or 'Unknown',
            'listing_date': vehicle.created_at.isoformat() if vehicle.created_at else None
        }
        
        # Scoring analysis
        if isinstance(score_data, dict):
            scoring_data = {
                'overall_score': score_data.get('overall_score', 0),
                'component_scores': score_data.get('component_scores', {}),
                'market_position': score_data.get('market_position', 'unknown'),
                'percentile_rank': score_data.get('percentile_rank', 0),
                'recommended_action': score_data.get('recommended_action', 'hold')
            }
        else:
            scoring_data = {
                'overall_score': getattr(score_data, 'overall_score', 0) if score_data else 0,
                'component_scores': {
                    'price_score': getattr(score_data, 'price_score', 0) if score_data else 0,
                    'age_score': getattr(score_data, 'age_score', 0) if score_data else 0,
                    'scarcity_score': getattr(score_data, 'scarcity_score', 0) if score_data else 0
                },
                'market_position': getattr(score_data, 'market_position', 'unknown') if score_data else 'unknown',
                'percentile_rank': getattr(score_data, 'percentile_rank', 0) if score_data else 0,
                'recommended_action': getattr(score_data, 'recommended_action', 'hold') if score_data else 'hold'
            }
        
        # Comparable vehicles
        comparable_vehicles = []
        for match in matches[:5]:
            if 'vehicle' in match:
                comp = match['vehicle']
                comparable_vehicles.append({
                    'year': comp.get('year') or 0,
                    'make': comp.get('make') or 'Unknown',
                    'model': comp.get('model') or 'Unknown',
                    'trim': comp.get('trim') or '',
                    'condition': comp.get('condition') or 'Unknown',
                    'mileage': comp.get('mileage') or 0,
                    'price': comp.get('price') or 0,
                    'similarity_score': match.get('similarity_score', 0),
                    'dealer': comp.get('dealer_name') or 'Unknown'
                })
        
        return {
            'target_vehicle': vehicle_data,
            'scoring_analysis': scoring_data,
            'comparable_vehicles': comparable_vehicles,
            'market_context': {
                'total_comparables': len(matches),
                'analysis_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'market_segment': f"{vehicle.make} {vehicle.model}",
                'price_range': self._determine_price_range(vehicle.price)
            }
        }
    
    def _create_ai_prompt(self, context: Dict) -> str:
        """Create detailed prompt for AI analysis"""
        
        try:
            vehicle = context['target_vehicle']
            scores = context['scoring_analysis']
            comparables = context['comparable_vehicles']
            
            # Safely extract vehicle information with defaults
            year = vehicle.get('year', 'Unknown')
            make = vehicle.get('make', 'Unknown')
            model = vehicle.get('model', 'Unknown')
            trim = vehicle.get('trim', '') or ''
            condition = vehicle.get('condition', 'Unknown')
            mileage = vehicle.get('mileage', 0) or 0
            price = vehicle.get('price', 0) or 0
            dealer = vehicle.get('dealer', 'Unknown')
            
            # Safely extract scores with defaults
            overall_score = scores.get('overall_score', 0) or 0
            component_scores = scores.get('component_scores', {})
            price_score = component_scores.get('price_score', 0) or 0
            age_score = component_scores.get('age_score', 0) or 0
            scarcity_score = component_scores.get('scarcity_score', 0) or 0
            market_position = scores.get('market_position', 'Unknown')
            percentile_rank = scores.get('percentile_rank', 0) or 0
            recommended_action = scores.get('recommended_action', 'hold')
            
            prompt = f"""
Analyze the following vehicle for pricing intelligence and market positioning:

TARGET VEHICLE:
- {year} {make} {model} {trim}
- Condition: {condition}
- Mileage: {mileage:,} miles
- Current Price: ${price:,}
- Dealer: {dealer}

SCORING ANALYSIS:
- Overall Competitiveness Score: {overall_score:.1f}/100
- Price Score: {price_score:.1f}/100
- Age Score: {age_score:.1f}/100
- Scarcity Score: {scarcity_score:.1f}/100
- Market Position: {market_position}
- Percentile Rank: {percentile_rank:.1f}%
- Recommended Action: {recommended_action}

COMPARABLE VEHICLES ({len(comparables)} found):
"""
            
            for i, comp in enumerate(comparables[:3], 1):
                # Safely extract comparable vehicle data
                comp_year = comp.get('year', 'Unknown')
                comp_make = comp.get('make', 'Unknown')
                comp_model = comp.get('model', 'Unknown')
                comp_trim = comp.get('trim', '') or ''
                comp_price = comp.get('price', 0) or 0
                comp_mileage = comp.get('mileage', 0) or 0
                comp_condition = comp.get('condition', 'Unknown')
                comp_dealer = comp.get('dealer', 'Unknown')
                similarity_score = comp.get('similarity_score', 0) or 0
                
                prompt += f"""
{i}. {comp_year} {comp_make} {comp_model} {comp_trim}
   - Price: ${comp_price:,} | Mileage: {comp_mileage:,} | Similarity: {similarity_score:.1f}%
   - Condition: {comp_condition} | Dealer: {comp_dealer}
"""
            
            market_context = context.get('market_context', {})
            analysis_date = market_context.get('analysis_date', 'Unknown')
            market_segment = market_context.get('market_segment', 'Unknown')
            price_range = market_context.get('price_range', 'Unknown')
            total_comparables = market_context.get('total_comparables', 0)
            
            prompt += f"""
MARKET CONTEXT:
- Analysis Date: {analysis_date}
- Market Segment: {market_segment}
- Price Range: {price_range}
- Total Comparable Vehicles: {total_comparables}

Please provide a comprehensive analysis focusing on:
1. How competitive the current pricing is
2. Market positioning relative to comparable vehicles
3. Specific actionable recommendations for pricing strategy
4. Risk factors and opportunities
5. Timeline for implementing recommendations

Ensure all recommendations are specific, actionable, and based on the data provided.
"""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error creating AI prompt: {str(e)}")
            # Return a basic prompt as fallback
            return """
Analyze the provided vehicle data for pricing intelligence and market positioning.
Provide insights on pricing competitiveness, market position, and recommendations.
"""
    
    def _determine_price_range(self, price: float) -> str:
        """Determine price range category"""
        if price < 15000:
            return "Budget ($0-$15K)"
        elif price < 25000:
            return "Mid-Range ($15K-$25K)"
        elif price < 40000:
            return "Premium ($25K-$40K)"
        elif price < 60000:
            return "Luxury ($40K-$60K)"
        else:
            return "Ultra-Luxury ($60K+)"
    
    def _extract_score_summary(self, score_data: Any) -> Dict:
        """Extract score summary for context"""
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
    
    def generate_market_insights(self) -> Dict:
        """Generate market-level insights using AI"""
        
        logger.info("Generating market-level AI insights")
        
        # Get market data
        market_data = self.market_analyzer.get_market_overview()
        
        # Create market analysis prompt
        prompt = self._create_market_prompt(market_data)
        
        # Generate insights
        context = {'market_data': market_data}
        insights = self.llm_client.generate_insights(prompt, context)
        
        return {
            'market_insights': insights,
            'generated_at': datetime.utcnow().isoformat(),
            'ai_provider': self.ai_config.provider,
            'data_summary': market_data
        }
    
    def _create_market_prompt(self, market_data: Dict) -> str:
        """Create prompt for market-level analysis"""
        
        return f"""
Analyze the current automotive market conditions based on the following data:

MARKET OVERVIEW:
- Total Vehicles in Database: {market_data.get('total_vehicles', 0)}
- Average Price: ${market_data.get('average_price', 0):,.0f}
- Price Range: ${market_data.get('min_price', 0):,.0f} - ${market_data.get('max_price', 0):,.0f}
- Average Mileage: {market_data.get('average_mileage', 0):,.0f} miles
- Most Common Make: {market_data.get('top_make', 'Unknown')}
- Most Common Model: {market_data.get('top_model', 'Unknown')}

INVENTORY DISTRIBUTION:
- New Vehicles: {market_data.get('condition_distribution', {}).get('New', 0)}
- Used Vehicles: {market_data.get('condition_distribution', {}).get('Used', 0)}
- Certified Vehicles: {market_data.get('condition_distribution', {}).get('Certified', 0)}

Please provide market insights including:
1. Overall market health and trends
2. Pricing opportunities and challenges
3. Inventory recommendations
4. Strategic market positioning advice
5. Risk factors and opportunities in the current market

Focus on actionable insights for automotive dealerships.
"""

# Create global instance
insights_generator = EnhancedInsightsGenerator()

