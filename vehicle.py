"""
Vehicle data models for the pricing intelligence platform
"""

from src.models.user import db
from datetime import datetime
import json

class Vehicle(db.Model):
    """Main vehicle model for storing normalized vehicle data"""
    
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False, index=True)
    
    # Basic vehicle info
    year = db.Column(db.Integer, nullable=False, index=True)
    make = db.Column(db.String(50), nullable=False, index=True)
    model = db.Column(db.String(100), nullable=False, index=True)
    trim = db.Column(db.String(100), nullable=True)
    
    # Condition and specs
    condition = db.Column(db.String(20), nullable=False)  # New, Used, Certified
    mileage = db.Column(db.Integer, nullable=True)
    doors = db.Column(db.Integer, nullable=True)
    drivetrain = db.Column(db.String(20), nullable=True)
    transmission = db.Column(db.String(20), nullable=True)
    fuel_type = db.Column(db.String(20), nullable=True)
    vehicle_type = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    
    # Pricing info
    price = db.Column(db.Float, nullable=True)
    price_alt = db.Column(db.Float, nullable=True)
    discount = db.Column(db.Float, nullable=True)
    
    # Dealer info
    dealer_name = db.Column(db.String(200), nullable=False, index=True)
    stock_number = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    
    # URLs and images
    listing_url = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    
    # VIN decoded information (enriched data)
    vin_decoded = db.Column(db.Text, nullable=True)  # JSON string
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    snapshots = db.relationship('VehicleSnapshot', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Vehicle {self.year} {self.make} {self.model} - {self.vin}>'
    
    def to_dict(self):
        """Convert vehicle to dictionary"""
        return {
            'id': self.id,
            'vin': self.vin,
            'year': self.year,
            'make': self.make,
            'model': self.model,
            'trim': self.trim,
            'condition': self.condition,
            'mileage': self.mileage,
            'doors': self.doors,
            'drivetrain': self.drivetrain,
            'transmission': self.transmission,
            'fuel_type': self.fuel_type,
            'vehicle_type': self.vehicle_type,
            'color': self.color,
            'price': self.price,
            'price_alt': self.price_alt,
            'discount': self.discount,
            'dealer_name': self.dealer_name,
            'stock_number': self.stock_number,
            'location': self.location,
            'listing_url': self.listing_url,
            'image_url': self.image_url,
            'vin_decoded': json.loads(self.vin_decoded) if self.vin_decoded else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

class VehicleSnapshot(db.Model):
    """Historical snapshots of vehicle data for tracking changes"""
    
    __tablename__ = 'vehicle_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    
    # Snapshot data (JSON)
    snapshot_data = db.Column(db.Text, nullable=False)  # Full vehicle data as JSON
    
    # Key fields for quick queries
    price = db.Column(db.Float, nullable=True, index=True)
    mileage = db.Column(db.Integer, nullable=True)
    condition = db.Column(db.String(20), nullable=True)
    
    # Metadata
    snapshot_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    change_type = db.Column(db.String(20), nullable=False)  # 'created', 'updated', 'price_change', 'removed'
    
    def __repr__(self):
        return f'<VehicleSnapshot {self.vehicle_id} - {self.snapshot_date}>'
    
    def to_dict(self):
        """Convert snapshot to dictionary"""
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'snapshot_data': json.loads(self.snapshot_data),
            'price': self.price,
            'mileage': self.mileage,
            'condition': self.condition,
            'snapshot_date': self.snapshot_date.isoformat(),
            'change_type': self.change_type
        }

class VehicleMatch(db.Model):
    """Store vehicle matching results for performance"""
    
    __tablename__ = 'vehicle_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    source_vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    match_vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    
    # Matching scores
    similarity_score = db.Column(db.Float, nullable=False, index=True)
    exact_match = db.Column(db.Boolean, default=False)
    
    # Match criteria
    year_match = db.Column(db.Boolean, default=False)
    make_match = db.Column(db.Boolean, default=False)
    model_match = db.Column(db.Boolean, default=False)
    trim_match = db.Column(db.Boolean, default=False)
    condition_match = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_vehicle = db.relationship('Vehicle', foreign_keys=[source_vehicle_id], backref='source_matches')
    match_vehicle = db.relationship('Vehicle', foreign_keys=[match_vehicle_id], backref='target_matches')
    
    def __repr__(self):
        return f'<VehicleMatch {self.source_vehicle_id} -> {self.match_vehicle_id} ({self.similarity_score:.2f})>'
    
    def to_dict(self):
        """Convert match to dictionary"""
        return {
            'id': self.id,
            'source_vehicle_id': self.source_vehicle_id,
            'match_vehicle_id': self.match_vehicle_id,
            'similarity_score': self.similarity_score,
            'exact_match': self.exact_match,
            'year_match': self.year_match,
            'make_match': self.make_match,
            'model_match': self.model_match,
            'trim_match': self.trim_match,
            'condition_match': self.condition_match,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class VehicleScore(db.Model):
    """Store calculated pricing scores for vehicles"""
    
    __tablename__ = 'vehicle_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, unique=True)
    
    # Scoring components
    price_score = db.Column(db.Float, nullable=True)  # 0-100, price competitiveness
    age_score = db.Column(db.Float, nullable=True)    # 0-100, age factor
    scarcity_score = db.Column(db.Float, nullable=True)  # 0-100, market scarcity
    
    # Overall score
    overall_score = db.Column(db.Float, nullable=False, index=True)  # 0-100, weighted average
    
    # Market position
    market_position = db.Column(db.String(20), nullable=True)  # 'underpriced', 'competitive', 'overpriced'
    percentile_rank = db.Column(db.Float, nullable=True)  # 0-100, percentile in market
    
    # Recommendations
    recommended_action = db.Column(db.String(50), nullable=True)  # 'reduce_price', 'hold', 'increase_price'
    price_adjustment = db.Column(db.Float, nullable=True)  # Suggested price change
    
    # Metadata
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    vehicle = db.relationship('Vehicle', backref=db.backref('score', uselist=False))
    
    def __repr__(self):
        return f'<VehicleScore {self.vehicle_id} - {self.overall_score:.1f}>'
    
    def to_dict(self):
        """Convert score to dictionary"""
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'price_score': self.price_score,
            'age_score': self.age_score,
            'scarcity_score': self.scarcity_score,
            'overall_score': self.overall_score,
            'market_position': self.market_position,
            'percentile_rank': self.percentile_rank,
            'recommended_action': self.recommended_action,
            'price_adjustment': self.price_adjustment,
            'calculated_at': self.calculated_at.isoformat()
        }

