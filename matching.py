"""
API routes for vehicle matching and market analysis
"""

from flask import Blueprint, request, jsonify
from src.services.matching import VehicleMatchingEngine, MarketAnalyzer
from src.models.vehicle import db, Vehicle, VehicleMatch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

matching_bp = Blueprint('matching', __name__)

# Initialize services
matching_engine = VehicleMatchingEngine()
market_analyzer = MarketAnalyzer()

@matching_bp.route('/find-matches/<vin>', methods=['POST'])
def find_matches(vin):
    """
    Find matches for a specific vehicle by VIN
    """
    try:
        # Get the target vehicle
        vehicle = Vehicle.query.filter_by(vin=vin.upper()).first()
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Get parameters
        data = request.get_json() or {}
        min_similarity = data.get('min_similarity', 0.3)
        max_matches = data.get('max_matches', 10)
        exclude_same_dealer = data.get('exclude_same_dealer', True)
        store_results = data.get('store_results', True)
        
        # Find matches
        if store_results:
            result = matching_engine.find_and_store_matches(
                vehicle,
                min_similarity=min_similarity,
                max_matches=max_matches,
                exclude_same_dealer=exclude_same_dealer
            )
            
            # Get the stored matches
            matches = matching_engine.get_stored_matches(vehicle, max_matches)
            
            return jsonify({
                'success': True,
                'target_vehicle': vehicle.to_dict(),
                'matches': matches,
                'summary': result
            }), 200
        else:
            matches = matching_engine.find_matches(
                vehicle,
                min_similarity=min_similarity,
                max_matches=max_matches,
                exclude_same_dealer=exclude_same_dealer
            )
            
            # Convert matches to serializable format
            serialized_matches = []
            for match in matches:
                serialized_matches.append({
                    'vehicle': match['vehicle'].to_dict(),
                    'similarity_score': match['similarity_score'],
                    'component_scores': match['component_scores'],
                    'exact_match': match['exact_match'],
                    'year_match': match['year_match'],
                    'make_match': match['make_match'],
                    'model_match': match['model_match'],
                    'trim_match': match['trim_match'],
                    'condition_match': match['condition_match']
                })
            
            return jsonify({
                'success': True,
                'target_vehicle': vehicle.to_dict(),
                'matches': serialized_matches
            }), 200
    
    except Exception as e:
        logger.error(f"Error finding matches for VIN {vin}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@matching_bp.route('/matches/<vin>', methods=['GET'])
def get_matches(vin):
    """
    Get stored matches for a vehicle by VIN
    """
    try:
        # Get the target vehicle
        vehicle = Vehicle.query.filter_by(vin=vin.upper()).first()
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Get parameters
        limit = request.args.get('limit', 10, type=int)
        
        # Get stored matches
        matches = matching_engine.get_stored_matches(vehicle, limit)
        
        return jsonify({
            'success': True,
            'target_vehicle': vehicle.to_dict(),
            'matches': matches,
            'count': len(matches)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting matches for VIN {vin}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@matching_bp.route('/batch-match', methods=['POST'])
def batch_match():
    """
    Run batch matching for multiple vehicles
    """
    try:
        data = request.get_json() or {}
        
        # Get parameters
        vehicle_ids = data.get('vehicle_ids')  # None for all vehicles
        batch_size = data.get('batch_size', 50)
        min_similarity = data.get('min_similarity', 0.3)
        max_matches = data.get('max_matches', 10)
        exclude_same_dealer = data.get('exclude_same_dealer', True)
        
        # Run batch matching
        result = matching_engine.batch_find_matches(
            vehicle_ids=vehicle_ids,
            batch_size=batch_size,
            min_similarity=min_similarity,
            max_matches=max_matches,
            exclude_same_dealer=exclude_same_dealer
        )
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
    
    except Exception as e:
        logger.error(f"Error in batch matching: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@matching_bp.route('/market-analysis/<vin>', methods=['GET'])
def market_analysis(vin):
    """
    Get market analysis for a specific vehicle
    """
    try:
        # Get the target vehicle
        vehicle = Vehicle.query.filter_by(vin=vin.upper()).first()
        
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Perform market analysis
        analysis = market_analyzer.analyze_vehicle_market_position(vehicle)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    
    except Exception as e:
        logger.error(f"Error in market analysis for VIN {vin}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@matching_bp.route('/similarity', methods=['POST'])
def calculate_similarity():
    """
    Calculate similarity between two vehicles by VIN
    """
    try:
        data = request.get_json()
        
        if not data or 'vin1' not in data or 'vin2' not in data:
            return jsonify({'error': 'Both vin1 and vin2 are required'}), 400
        
        # Get vehicles
        vehicle1 = Vehicle.query.filter_by(vin=data['vin1'].upper()).first()
        vehicle2 = Vehicle.query.filter_by(vin=data['vin2'].upper()).first()
        
        if not vehicle1:
            return jsonify({'error': f'Vehicle with VIN {data["vin1"]} not found'}), 404
        
        if not vehicle2:
            return jsonify({'error': f'Vehicle with VIN {data["vin2"]} not found'}), 404
        
        # Calculate similarity
        similarity_score, component_scores = matching_engine.similarity_calculator.calculate_overall_similarity(
            vehicle1, vehicle2
        )
        
        return jsonify({
            'success': True,
            'vehicle1': vehicle1.to_dict(),
            'vehicle2': vehicle2.to_dict(),
            'similarity_score': similarity_score,
            'component_scores': component_scores
        }), 200
    
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@matching_bp.route('/matching-stats', methods=['GET'])
def matching_stats():
    """
    Get matching statistics
    """
    try:
        # Vehicle counts
        total_vehicles = Vehicle.query.count()
        
        # Matching statistics
        total_matches = VehicleMatch.query.count()
        vehicles_with_matches = db.session.query(VehicleMatch.source_vehicle_id).distinct().count()
        
        # Average matches per vehicle
        avg_matches = total_matches / vehicles_with_matches if vehicles_with_matches > 0 else 0
        
        # Similarity score distribution
        similarity_stats = db.session.query(
            db.func.min(VehicleMatch.similarity_score).label('min_similarity'),
            db.func.max(VehicleMatch.similarity_score).label('max_similarity'),
            db.func.avg(VehicleMatch.similarity_score).label('avg_similarity')
        ).first()
        
        # Exact matches count
        exact_matches = VehicleMatch.query.filter_by(exact_match=True).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_vehicles': total_vehicles,
                'total_matches': total_matches,
                'vehicles_with_matches': vehicles_with_matches,
                'vehicles_without_matches': total_vehicles - vehicles_with_matches,
                'avg_matches_per_vehicle': round(avg_matches, 2),
                'exact_matches': exact_matches,
                'similarity_stats': {
                    'min_similarity': float(similarity_stats.min_similarity) if similarity_stats.min_similarity else None,
                    'max_similarity': float(similarity_stats.max_similarity) if similarity_stats.max_similarity else None,
                    'avg_similarity': float(similarity_stats.avg_similarity) if similarity_stats.avg_similarity else None
                }
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting matching stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@matching_bp.route('/test-matching', methods=['POST'])
def test_matching():
    """
    Test the matching engine with a sample of vehicles
    """
    try:
        data = request.get_json() or {}
        sample_size = data.get('sample_size', 5)
        
        # Get a sample of vehicles
        vehicles = Vehicle.query.limit(sample_size).all()
        
        if not vehicles:
            return jsonify({'error': 'No vehicles found for testing'}), 404
        
        results = []
        for vehicle in vehicles:
            try:
                # Find matches
                matches = matching_engine.find_matches(
                    vehicle, 
                    min_similarity=0.3, 
                    max_matches=5,
                    exclude_same_dealer=True
                )
                
                # Perform market analysis
                analysis = market_analyzer.analyze_vehicle_market_position(vehicle)
                
                results.append({
                    'vehicle': {
                        'vin': vehicle.vin,
                        'year': vehicle.year,
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'price': vehicle.price
                    },
                    'matches_found': len(matches),
                    'best_match_similarity': matches[0]['similarity_score'] if matches else 0,
                    'market_position': analysis.get('market_position', 'unknown')
                })
                
            except Exception as e:
                results.append({
                    'vehicle': {
                        'vin': vehicle.vin,
                        'year': vehicle.year,
                        'make': vehicle.make,
                        'model': vehicle.model,
                        'price': vehicle.price
                    },
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'test_results': results,
            'sample_size': len(results)
        }), 200
    
    except Exception as e:
        logger.error(f"Error in test matching: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

