"""
Data ingestion service for processing inventory CSV files
Handles CSV parsing, VIN decoding, data normalization, and database storage
"""

import pandas as pd
import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from src.models.vehicle import db, Vehicle, VehicleSnapshot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VINDecoder:
    """VIN decoding service using NHTSA API"""
    
    NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/decodevin"
    
    @staticmethod
    def decode_vin(vin: str) -> Optional[Dict]:
        """
        Decode VIN using NHTSA API
        Returns decoded information or None if decoding fails
        """
        if not vin or len(vin) != 17:
            logger.warning(f"Invalid VIN length: {vin}")
            return None
        
        try:
            # Clean VIN
            vin = vin.upper().strip()
            
            # Call NHTSA API
            url = f"{VINDecoder.NHTSA_API_URL}/{vin}?format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('Count', 0) == 0:
                logger.warning(f"No data returned for VIN: {vin}")
                return None
            
            # Extract relevant information
            results = data.get('Results', [])
            decoded_info = {}
            
            for result in results:
                variable = result.get('Variable', '')
                value = result.get('Value', '')
                
                if value and value != 'Not Applicable':
                    # Map important fields
                    if 'Make' in variable:
                        decoded_info['make'] = value
                    elif 'Model' in variable:
                        decoded_info['model'] = value
                    elif 'Model Year' in variable:
                        try:
                            decoded_info['year'] = int(value)
                        except ValueError:
                            pass
                    elif 'Trim' in variable:
                        decoded_info['trim'] = value
                    elif 'Body Class' in variable:
                        decoded_info['body_class'] = value
                    elif 'Vehicle Type' in variable:
                        decoded_info['vehicle_type'] = value
                    elif 'Fuel Type' in variable:
                        decoded_info['fuel_type'] = value
                    elif 'Engine' in variable:
                        decoded_info['engine'] = value
                    elif 'Transmission' in variable:
                        decoded_info['transmission'] = value
                    elif 'Drive Type' in variable:
                        decoded_info['drivetrain'] = value
                    elif 'Doors' in variable:
                        try:
                            decoded_info['doors'] = int(value)
                        except ValueError:
                            pass
            
            decoded_info['vin'] = vin
            decoded_info['decoded_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Successfully decoded VIN: {vin}")
            return decoded_info
            
        except requests.RequestException as e:
            logger.error(f"Error decoding VIN {vin}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error decoding VIN {vin}: {e}")
            return None

class DataNormalizer:
    """Data normalization and cleaning utilities"""
    
    @staticmethod
    def normalize_make(make: str) -> str:
        """Normalize vehicle make"""
        if not make:
            return make
        
        # Convert to uppercase and strip
        make = make.upper().strip()
        
        # Common normalizations
        make_mappings = {
            'CHEVROLET': 'CHEVROLET',
            'CHEVY': 'CHEVROLET',
            'GMC': 'GMC',
            'CADILLAC': 'CADILLAC',
            'BUICK': 'BUICK',
            'FORD': 'FORD',
            'LINCOLN': 'LINCOLN',
            'TOYOTA': 'TOYOTA',
            'LEXUS': 'LEXUS',
            'HONDA': 'HONDA',
            'ACURA': 'ACURA',
            'NISSAN': 'NISSAN',
            'INFINITI': 'INFINITI',
            'HYUNDAI': 'HYUNDAI',
            'KIA': 'KIA',
            'GENESIS': 'GENESIS',
            'VOLKSWAGEN': 'VOLKSWAGEN',
            'VW': 'VOLKSWAGEN',
            'AUDI': 'AUDI',
            'BMW': 'BMW',
            'MERCEDES-BENZ': 'MERCEDES-BENZ',
            'MERCEDES': 'MERCEDES-BENZ',
            'JEEP': 'JEEP',
            'CHRYSLER': 'CHRYSLER',
            'DODGE': 'DODGE',
            'RAM': 'RAM',
            'SUBARU': 'SUBARU',
            'MAZDA': 'MAZDA',
            'MITSUBISHI': 'MITSUBISHI',
            'VOLVO': 'VOLVO'
        }
        
        return make_mappings.get(make, make)
    
    @staticmethod
    def normalize_model(model: str) -> str:
        """Normalize vehicle model"""
        if not model:
            return model
        
        # Convert to uppercase and strip
        model = model.upper().strip()
        
        # Remove common prefixes/suffixes
        model = re.sub(r'^(NEW|USED|CERTIFIED)\s+', '', model)
        model = re.sub(r'\s+(SEDAN|COUPE|HATCHBACK|SUV|TRUCK|WAGON)$', '', model)
        
        return model
    
    @staticmethod
    def normalize_condition(condition: str) -> str:
        """Normalize vehicle condition"""
        if not condition:
            return 'Unknown'
        
        condition = condition.upper().strip()
        
        if 'NEW' in condition:
            return 'New'
        elif 'CERTIFIED' in condition or 'CPO' in condition:
            return 'Certified'
        elif 'USED' in condition:
            return 'Used'
        else:
            return condition.title()
    
    @staticmethod
    def clean_price(price_str) -> Optional[float]:
        """Clean and convert price string to float"""
        if pd.isna(price_str) or price_str == '':
            return None
        
        if isinstance(price_str, (int, float)):
            return float(price_str) if price_str > 0 else None
        
        # Remove currency symbols and formatting
        price_str = str(price_str).replace('$', '').replace(',', '').strip()
        
        try:
            price = float(price_str)
            return price if price > 0 else None
        except ValueError:
            return None
    
    @staticmethod
    def clean_mileage(mileage) -> Optional[int]:
        """Clean and convert mileage to integer"""
        if pd.isna(mileage) or mileage == '':
            return None
        
        if isinstance(mileage, (int, float)):
            return int(mileage) if mileage >= 0 else None
        
        # Remove formatting
        mileage_str = str(mileage).replace(',', '').strip()
        
        try:
            mileage_val = int(float(mileage_str))
            return mileage_val if mileage_val >= 0 else None
        except ValueError:
            return None

class InventoryIngestionService:
    """Main service for ingesting inventory CSV data"""
    
    def __init__(self):
        self.vin_decoder = VINDecoder()
        self.normalizer = DataNormalizer()
    
    def process_csv(self, csv_path: str, dealer_name: Optional[str] = None) -> Dict:
        """
        Process inventory CSV file and store in database
        Returns summary of processing results
        """
        logger.info(f"Starting CSV processing: {csv_path}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} records from CSV")
            
            # Process each row
            results = {
                'total_records': len(df),
                'processed': 0,
                'created': 0,
                'updated': 0,
                'errors': 0,
                'error_details': []
            }
            
            for index, row in df.iterrows():
                try:
                    result = self._process_vehicle_record(row, dealer_name)
                    results['processed'] += 1
                    
                    if result == 'created':
                        results['created'] += 1
                    elif result == 'updated':
                        results['updated'] += 1
                        
                except Exception as e:
                    results['errors'] += 1
                    error_msg = f"Row {index}: {str(e)}"
                    results['error_details'].append(error_msg)
                    logger.error(error_msg)
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"CSV processing complete: {results}")
            return results
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing CSV: {e}")
            raise
    
    def _process_vehicle_record(self, row: pd.Series, dealer_name: Optional[str] = None) -> str:
        """
        Process a single vehicle record
        Returns 'created' or 'updated'
        """
        # Extract and clean data
        vin = str(row.get('VIN', '')).strip().upper()
        
        if not vin or len(vin) != 17:
            raise ValueError(f"Invalid VIN: {vin}")
        
        # Check if vehicle exists
        existing_vehicle = Vehicle.query.filter_by(vin=vin).first()
        
        # Prepare vehicle data
        vehicle_data = self._extract_vehicle_data(row, dealer_name)
        
        if existing_vehicle:
            # Update existing vehicle
            self._update_vehicle(existing_vehicle, vehicle_data)
            return 'updated'
        else:
            # Create new vehicle
            self._create_vehicle(vehicle_data)
            return 'created'
    
    def _extract_vehicle_data(self, row: pd.Series, dealer_name: Optional[str] = None) -> Dict:
        """Extract and normalize vehicle data from CSV row"""
        
        # Basic info
        vin = str(row.get('VIN', '')).strip().upper()
        year = int(row.get('Year', 0)) if pd.notna(row.get('Year')) else None
        make = self.normalizer.normalize_make(str(row.get('Make', '')))
        model = self.normalizer.normalize_model(str(row.get('Model', '')))
        trim = str(row.get('Trim', '')).strip() if pd.notna(row.get('Trim')) else None
        
        # Condition and specs
        condition = self.normalizer.normalize_condition(str(row.get('Condition', '')))
        mileage = self.normalizer.clean_mileage(row.get('Mileage'))
        doors = int(row.get('Doors', 0)) if pd.notna(row.get('Doors')) else None
        drivetrain = str(row.get('Drivetrain', '')).strip() if pd.notna(row.get('Drivetrain')) else None
        transmission = str(row.get('Transmission', '')).strip() if pd.notna(row.get('Transmission')) else None
        fuel_type = str(row.get('Fuel Type', '')).strip() if pd.notna(row.get('Fuel Type')) else None
        vehicle_type = str(row.get('Vehicle Type', '')).strip() if pd.notna(row.get('Vehicle Type')) else None
        color = str(row.get('Color', '')).strip() if pd.notna(row.get('Color')) else None
        
        # Pricing
        price = self.normalizer.clean_price(row.get('Price'))
        price_alt = self.normalizer.clean_price(row.get('Price alt.'))
        discount = self.normalizer.clean_price(row.get('Discount'))
        
        # Dealer info
        dealer = dealer_name or str(row.get('Advertiser Name', '')).strip()
        stock_number = str(row.get('stock_number', '')).strip() if pd.notna(row.get('stock_number')) else None
        location = str(row.get('Location', '')).strip() if pd.notna(row.get('Location')) else None
        
        # URLs
        listing_url = str(row.get('URL', '')).strip() if pd.notna(row.get('URL')) else None
        image_url = str(row.get('Image URL', '')).strip() if pd.notna(row.get('Image URL')) else None
        
        return {
            'vin': vin,
            'year': year,
            'make': make,
            'model': model,
            'trim': trim,
            'condition': condition,
            'mileage': mileage,
            'doors': doors,
            'drivetrain': drivetrain,
            'transmission': transmission,
            'fuel_type': fuel_type,
            'vehicle_type': vehicle_type,
            'color': color,
            'price': price,
            'price_alt': price_alt,
            'discount': discount,
            'dealer_name': dealer,
            'stock_number': stock_number,
            'location': location,
            'listing_url': listing_url,
            'image_url': image_url
        }
    
    def _create_vehicle(self, vehicle_data: Dict) -> Vehicle:
        """Create new vehicle record"""
        
        # Decode VIN
        vin_decoded = self.vin_decoder.decode_vin(vehicle_data['vin'])
        
        # Create vehicle
        vehicle = Vehicle(
            vin=vehicle_data['vin'],
            year=vehicle_data['year'],
            make=vehicle_data['make'],
            model=vehicle_data['model'],
            trim=vehicle_data['trim'],
            condition=vehicle_data['condition'],
            mileage=vehicle_data['mileage'],
            doors=vehicle_data['doors'],
            drivetrain=vehicle_data['drivetrain'],
            transmission=vehicle_data['transmission'],
            fuel_type=vehicle_data['fuel_type'],
            vehicle_type=vehicle_data['vehicle_type'],
            color=vehicle_data['color'],
            price=vehicle_data['price'],
            price_alt=vehicle_data['price_alt'],
            discount=vehicle_data['discount'],
            dealer_name=vehicle_data['dealer_name'],
            stock_number=vehicle_data['stock_number'],
            location=vehicle_data['location'],
            listing_url=vehicle_data['listing_url'],
            image_url=vehicle_data['image_url'],
            vin_decoded=json.dumps(vin_decoded) if vin_decoded else None
        )
        
        db.session.add(vehicle)
        db.session.flush()  # Get the ID
        
        # Create initial snapshot
        self._create_snapshot(vehicle, 'created')
        
        logger.info(f"Created vehicle: {vehicle.vin}")
        return vehicle
    
    def _update_vehicle(self, vehicle: Vehicle, vehicle_data: Dict) -> Vehicle:
        """Update existing vehicle record"""
        
        # Check for changes
        changes = []
        
        # Update fields and track changes
        for field, new_value in vehicle_data.items():
            if field == 'vin':
                continue  # Don't update VIN
            
            old_value = getattr(vehicle, field)
            if old_value != new_value:
                changes.append(f"{field}: {old_value} -> {new_value}")
                setattr(vehicle, field, new_value)
        
        # Update timestamps
        vehicle.updated_at = datetime.utcnow()
        vehicle.last_seen = datetime.utcnow()
        
        # Create snapshot if there were changes
        if changes:
            change_type = 'price_change' if any('price' in change for change in changes) else 'updated'
            self._create_snapshot(vehicle, change_type)
            logger.info(f"Updated vehicle {vehicle.vin}: {', '.join(changes)}")
        else:
            # Just update last_seen
            logger.debug(f"No changes for vehicle: {vehicle.vin}")
        
        return vehicle
    
    def _create_snapshot(self, vehicle: Vehicle, change_type: str):
        """Create a historical snapshot of the vehicle"""
        
        snapshot_data = vehicle.to_dict()
        
        snapshot = VehicleSnapshot(
            vehicle_id=vehicle.id,
            snapshot_data=json.dumps(snapshot_data),
            price=vehicle.price,
            mileage=vehicle.mileage,
            condition=vehicle.condition,
            change_type=change_type
        )
        
        db.session.add(snapshot)
        logger.debug(f"Created snapshot for vehicle {vehicle.vin}: {change_type}")

