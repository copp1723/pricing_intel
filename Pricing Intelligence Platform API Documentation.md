# Pricing Intelligence Platform API Documentation

## Overview

The Pricing Intelligence Platform provides a comprehensive REST API for automotive dealership competitive pricing analysis. The API enables vehicle data ingestion, matching, scoring, and AI-powered insights generation.

**Base URL:** `http://localhost:5001/api`

## Authentication

Currently, the API operates without authentication for development purposes. In production, implement JWT or API key authentication.

## API Endpoints

### Health Check

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-17T01:00:00.000Z"
}
```

---

### Data Ingestion

#### POST /process-sample
Process the sample CSV inventory data.

**Request Body:**
```json
{
  "dealer_name": "World Hyundai of Matteson"
}
```

**Response:**
```json
{
  "success": true,
  "message": "CSV processing complete",
  "summary": {
    "total_records": 363,
    "processed": 363,
    "created": 363,
    "updated": 0,
    "errors": 0
  }
}
```

#### POST /upload-csv
Upload and process custom CSV inventory data.

**Request:** Multipart form data with CSV file

**Response:**
```json
{
  "success": true,
  "message": "CSV processing complete",
  "summary": {
    "total_records": 100,
    "processed": 100,
    "created": 95,
    "updated": 5,
    "errors": 0
  }
}
```

#### GET /stats
Get ingestion statistics.

**Response:**
```json
{
  "total_vehicles": 363,
  "unique_makes": 15,
  "unique_models": 45,
  "price_range": {
    "min": 15000,
    "max": 65000,
    "avg": 28500
  },
  "last_updated": "2025-06-17T01:00:00.000Z"
}
```

---

### Vehicle Management

#### GET /vehicles
Get vehicles with filtering and pagination.

**Query Parameters:**
- `make` (string): Filter by make
- `model` (string): Filter by model
- `year` (integer): Filter by year
- `condition` (string): Filter by condition
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20)

**Response:**
```json
{
  "vehicles": [
    {
      "id": 1,
      "vin": "5NPEL4JA2LH042897",
      "year": 2020,
      "make": "HYUNDAI",
      "model": "SONATA",
      "trim": "SEL",
      "condition": "Certified",
      "mileage": 73405,
      "price": 17592.0,
      "dealer_name": "World Hyundai of Matteson",
      "created_at": "2025-06-17T00:49:34.642958"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 363,
    "pages": 19
  }
}
```

#### GET /vehicles/{vin}
Get specific vehicle by VIN.

**Response:**
```json
{
  "id": 1,
  "vin": "5NPEL4JA2LH042897",
  "year": 2020,
  "make": "HYUNDAI",
  "model": "SONATA",
  "trim": "SEL",
  "condition": "Certified",
  "mileage": 73405,
  "price": 17592.0,
  "dealer_name": "World Hyundai of Matteson",
  "vin_decoded": {
    "body_class": "Sedan/Saloon",
    "doors": 4,
    "fuel_type": "Gasoline",
    "make": "HYUNDAI",
    "model": "GDI THETA III"
  },
  "history": [
    {
      "price": 17592.0,
      "recorded_at": "2025-06-17T00:49:34.642958"
    }
  ]
}
```

---

### Vehicle Matching

#### POST /find-matches/{vin}
Find matching vehicles for a specific VIN.

**Request Body:**
```json
{
  "min_similarity": 0.3,
  "max_matches": 10,
  "exclude_same_dealer": true,
  "store_results": true
}
```

**Response:**
```json
{
  "success": true,
  "target_vehicle": {
    "vin": "5NPEL4JA2LH042897",
    "year": 2020,
    "make": "HYUNDAI",
    "model": "SONATA",
    "price": 17592.0
  },
  "matches": [
    {
      "vehicle": {
        "vin": "KMHL64JA3RA401653",
        "year": 2024,
        "make": "HYUNDAI",
        "model": "SONATA",
        "price": 27148.0
      },
      "similarity_score": 0.7,
      "exact_match": false,
      "component_scores": {
        "year": 0.6,
        "make": 1.0,
        "model": 1.0,
        "trim": 1.0
      }
    }
  ],
  "summary": {
    "matches_found": 5,
    "matches_stored": 5
  }
}
```

#### GET /matches/{vin}
Get stored matches for a vehicle.

**Query Parameters:**
- `limit` (integer): Maximum matches to return (default: 10)

#### POST /batch-match
Run batch matching for multiple vehicles.

**Request Body:**
```json
{
  "vehicle_ids": [1, 2, 3],
  "batch_size": 50,
  "min_similarity": 0.3,
  "max_matches": 10
}
```

#### GET /market-analysis/{vin}
Get market analysis for a specific vehicle.

**Response:**
```json
{
  "success": true,
  "analysis": {
    "vehicle_id": 1,
    "vin": "5NPEL4JA2LH042897",
    "target_price": 17592.0,
    "market_position": "competitive",
    "percentile_rank": 45.2,
    "market_stats": {
      "min_price": 15000,
      "max_price": 35000,
      "avg_price": 25000,
      "sample_size": 8
    }
  }
}
```

#### GET /matching-stats
Get matching engine statistics.

---

### Pricing Scoring

#### POST /calculate-score/{vin}
Calculate pricing score for a specific vehicle.

**Response:**
```json
{
  "success": true,
  "vehicle": {
    "vin": "5NPEL4JA2LH042897",
    "year": 2020,
    "make": "HYUNDAI",
    "model": "SONATA",
    "price": 17592.0
  },
  "score_analysis": {
    "overall_score": 47.1,
    "component_scores": {
      "price_score": 0.0,
      "age_score": 57.0,
      "scarcity_score": 100.0
    },
    "market_position": "below_average",
    "recommendations": {
      "primary_action": "monitor",
      "urgency": "medium",
      "reasoning": [
        "Vehicle rarity supports premium pricing",
        "Continue monitoring market conditions"
      ]
    }
  }
}
```

#### GET /score/{vin}
Get stored pricing score for a vehicle.

#### POST /batch-calculate
Calculate scores for multiple vehicles.

**Request Body:**
```json
{
  "vehicle_ids": [1, 2, 3],
  "batch_size": 50
}
```

#### GET /analytics
Get scoring analytics and statistics.

**Response:**
```json
{
  "success": true,
  "analytics": {
    "total_vehicles": 363,
    "scored_vehicles": 2,
    "coverage_pct": 0.55,
    "score_distribution": {
      "min_score": 33.0,
      "max_score": 57.0,
      "avg_score": 45.0
    },
    "market_positions": [
      {"position": "below_average", "count": 1},
      {"position": "average", "count": 1}
    ],
    "recommended_actions": [
      {"action": "monitor", "count": 2}
    ]
  }
}
```

#### GET /top-scores
Get vehicles with highest/lowest scores.

**Query Parameters:**
- `order` (string): 'desc' for highest, 'asc' for lowest
- `limit` (integer): Number of results
- `min_score` (float): Minimum score filter
- `max_score` (float): Maximum score filter

#### GET /recommendations
Get vehicles grouped by recommended actions.

**Query Parameters:**
- `action` (string): Filter by specific action
- `limit` (integer): Maximum results

#### GET /market-comparison
Get market comparison data.

**Query Parameters:**
- `make` (string): Filter by make
- `model` (string): Filter by model
- `year` (integer): Filter by year

---

### AI-Powered Insights

#### GET /vehicle-insights/{vin}
Generate comprehensive insights for a specific vehicle.

**Query Parameters:**
- `include_comparisons` (boolean): Include market comparisons (default: true)

**Response:**
```json
{
  "success": true,
  "insights": {
    "vehicle_id": 1,
    "vin": "5NPEL4JA2LH042897",
    "insights": {
      "executive_summary": "The 2020 HYUNDAI SONATA (Certified) priced at $17,592 currently holds a challenging competitive position...",
      "pricing_analysis": {
        "current_price": 17592.0,
        "price_competitiveness_score": 0,
        "comparable_avg_price": 28678.33,
        "price_difference_pct": -38.66,
        "pricing_insights": [
          "Price is 38.7% below comparable vehicles"
        ]
      },
      "market_positioning": {
        "market_position": "Unknown",
        "competitive_strengths": [],
        "competitive_weaknesses": [
          "Vehicle age may limit market appeal",
          "Overall competitive position needs improvement"
        ],
        "market_dynamics": [
          "Moderate comparable inventory indicates balanced market conditions"
        ]
      },
      "recommendations": {
        "primary_actions": [
          "Conduct comprehensive pricing review",
          "Consider price reduction to improve competitiveness"
        ],
        "secondary_actions": [
          "Gather more market data for better pricing insights",
          "Track vehicle performance metrics weekly"
        ],
        "timeline": "immediate",
        "expected_impact": "high"
      },
      "risk_factors": [
        "Vehicle age may lead to accelerated depreciation",
        "Poor competitive position may result in extended time on lot"
      ],
      "opportunities": [
        "Seasonal demand patterns may create pricing opportunities",
        "Targeted marketing can highlight vehicle's competitive advantages"
      ]
    }
  }
}
```

#### GET /market-insights
Generate market-level insights.

**Query Parameters:**
- `make` (string): Filter by make
- `model` (string): Filter by model
- `year` (integer): Filter by year

**Response:**
```json
{
  "success": true,
  "market_insights": {
    "market_overview": "Market analysis covers 363 vehicles with 2 scored for competitiveness...",
    "pricing_trends": {
      "trend_direction": "stable",
      "price_volatility": "moderate",
      "market_sentiment": "neutral"
    },
    "inventory_analysis": {
      "inventory_health": "needs_attention",
      "attention_required": 1,
      "well_positioned": 0
    },
    "strategic_recommendations": [
      "Expand scoring coverage to include all inventory",
      "Implement regular competitive pricing reviews"
    ]
  }
}
```

#### POST /batch-insights
Generate insights for multiple vehicles.

**Request Body:**
```json
{
  "vins": ["5NPEL4JA2LH042897", "KMHL64JA3RA401653"],
  "limit": 10,
  "include_comparisons": true
}
```

#### GET /insights-summary
Get insights engine capabilities and status.

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

Currently no rate limiting is implemented. In production, implement appropriate rate limiting based on usage patterns.

## Data Models

### Vehicle
```json
{
  "id": 1,
  "vin": "5NPEL4JA2LH042897",
  "year": 2020,
  "make": "HYUNDAI",
  "model": "SONATA",
  "trim": "SEL",
  "condition": "Certified",
  "mileage": 73405,
  "price": 17592.0,
  "price_alt": 17592.0,
  "dealer_name": "World Hyundai of Matteson",
  "stock_number": "WV15258",
  "color": "Grey",
  "doors": 4,
  "drivetrain": "FWD",
  "fuel_type": "Gasoline",
  "transmission": "Automatic",
  "vehicle_type": "Car_Truck",
  "image_url": "https://...",
  "listing_url": "http://...",
  "location": null,
  "discount": null,
  "vin_decoded": {},
  "created_at": "2025-06-17T00:49:34.642958",
  "updated_at": "2025-06-17T00:49:34.642961",
  "last_seen": "2025-06-17T00:49:34.642962"
}
```

### Vehicle Score
```json
{
  "id": 1,
  "vehicle_id": 1,
  "overall_score": 47.1,
  "price_score": 0.0,
  "age_score": 57.0,
  "scarcity_score": 100.0,
  "market_position": "below_average",
  "percentile_rank": null,
  "recommended_action": "monitor",
  "price_adjustment": null,
  "calculated_at": "2025-06-17T00:59:26.089239"
}
```

### Vehicle Match
```json
{
  "id": 1,
  "source_vehicle_id": 1,
  "match_vehicle_id": 2,
  "similarity_score": 0.7,
  "exact_match": false,
  "year_match": false,
  "make_match": true,
  "model_match": true,
  "trim_match": true,
  "condition_match": false,
  "created_at": "2025-06-17T00:56:04.585505",
  "updated_at": "2025-06-17T00:56:04.585509"
}
```

## Usage Examples

### Basic Workflow

1. **Upload Data:**
   ```bash
   curl -X POST http://localhost:5001/api/process-sample \
     -H "Content-Type: application/json" \
     -d '{"dealer_name": "My Dealership"}'
   ```

2. **Find Matches:**
   ```bash
   curl -X POST http://localhost:5001/api/find-matches/5NPEL4JA2LH042897 \
     -H "Content-Type: application/json" \
     -d '{"min_similarity": 0.3, "max_matches": 5}'
   ```

3. **Calculate Score:**
   ```bash
   curl -X POST http://localhost:5001/api/calculate-score/5NPEL4JA2LH042897
   ```

4. **Generate Insights:**
   ```bash
   curl -X GET http://localhost:5001/api/vehicle-insights/5NPEL4JA2LH042897
   ```

### Batch Processing

```bash
# Batch matching
curl -X POST http://localhost:5001/api/batch-match \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 50, "min_similarity": 0.3}'

# Batch scoring
curl -X POST http://localhost:5001/api/batch-calculate \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 50}'
```

## Development Notes

- The API is built with Flask and SQLAlchemy
- CORS is enabled for all origins
- Database is SQLite for development
- All timestamps are in UTC ISO format
- VIN lookups are case-insensitive
- Pagination uses 1-based indexing

## Production Considerations

1. **Authentication:** Implement JWT or API key authentication
2. **Rate Limiting:** Add rate limiting to prevent abuse
3. **Database:** Migrate to PostgreSQL or MySQL
4. **Caching:** Implement Redis for caching frequently accessed data
5. **Monitoring:** Add logging, metrics, and health checks
6. **Documentation:** Use OpenAPI/Swagger for interactive documentation
7. **Validation:** Add comprehensive input validation
8. **Security:** Implement HTTPS and security headers

