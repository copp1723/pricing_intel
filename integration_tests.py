#!/usr/bin/env python3
"""
Comprehensive integration tests for the Pricing Intelligence Platform
Tests all system components working together end-to-end
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5001/api"
FRONTEND_URL = "http://localhost:5173"
TEST_VIN = "5NPEL4JA2LH042897"

class PricingIntelligenceTests:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_api_health(self):
        """Test API health and connectivity"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("API Health Check", True, "API is responding")
                return True
            else:
                self.log_test("API Health Check", False, f"API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"API connection failed: {str(e)}")
            return False
    
    def test_data_ingestion(self):
        """Test data ingestion functionality"""
        try:
            # Check current stats
            response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                total_vehicles = stats.get('stats', {}).get('total_vehicles', 0)
                self.log_test("Data Ingestion Check", True, 
                            f"Found {total_vehicles} vehicles in database", 
                            {"total_vehicles": total_vehicles})
                return total_vehicles > 0
            else:
                self.log_test("Data Ingestion Check", False, "Failed to get stats")
                return False
        except Exception as e:
            self.log_test("Data Ingestion Check", False, f"Error: {str(e)}")
            return False
    
    def test_vehicle_matching(self):
        """Test vehicle matching engine"""
        try:
            # Test finding matches for a vehicle
            response = requests.post(f"{API_BASE_URL}/find-matches/{TEST_VIN}", 
                                   json={"min_similarity": 0.3, "max_matches": 5, "exclude_same_dealer": False},
                                   timeout=30)
            if response.status_code == 200:
                matches = response.json()
                match_count = len(matches.get('matches', []))
                self.log_test("Vehicle Matching", True, 
                            f"Found {match_count} matches for test vehicle",
                            {"match_count": match_count, "vin": TEST_VIN})
                return True
            else:
                self.log_test("Vehicle Matching", False, f"Matching failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Vehicle Matching", False, f"Error: {str(e)}")
            return False
    
    def test_pricing_scoring(self):
        """Test pricing scoring system"""
        try:
            # Calculate score for test vehicle
            response = requests.post(f"{API_BASE_URL}/calculate-score/{TEST_VIN}", timeout=30)
            if response.status_code == 200:
                score_data = response.json()
                score = score_data.get('score', {}).get('overall_score', 0)
                self.log_test("Pricing Scoring", True, 
                            f"Calculated score: {score:.1f} for test vehicle",
                            {"score": score, "vin": TEST_VIN})
                return True
            else:
                self.log_test("Pricing Scoring", False, f"Scoring failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pricing Scoring", False, f"Error: {str(e)}")
            return False
    
    def test_ai_insights(self):
        """Test AI insights generation"""
        try:
            # Generate insights for test vehicle
            response = requests.get(f"{API_BASE_URL}/vehicle-insights/{TEST_VIN}", timeout=60)
            if response.status_code == 200:
                insights = response.json()
                has_insights = ('insights' in insights and 
                              'insights' in insights['insights'] and 
                              'executive_summary' in insights['insights']['insights'])
                self.log_test("AI Insights Generation", has_insights, 
                            "Generated AI insights for test vehicle" if has_insights else "No insights generated",
                            {"has_insights": has_insights, "vin": TEST_VIN})
                return has_insights
            else:
                self.log_test("AI Insights Generation", False, f"Insights failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Insights Generation", False, f"Error: {str(e)}")
            return False
    
    def test_market_analysis(self):
        """Test market analysis functionality"""
        try:
            # Get market insights
            response = requests.get(f"{API_BASE_URL}/market-insights", timeout=30)
            if response.status_code == 200:
                market_data = response.json()
                has_insights = 'market_insights' in market_data
                self.log_test("Market Analysis", has_insights, 
                            "Generated market insights" if has_insights else "No market insights",
                            {"has_market_insights": has_insights})
                return has_insights
            else:
                self.log_test("Market Analysis", False, f"Market analysis failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Market Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_analytics_endpoints(self):
        """Test analytics and statistics endpoints"""
        try:
            endpoints = [
                ("/analytics", "Analytics"),
                ("/matching-stats", "Matching Statistics"),
                ("/stats", "General Statistics")
            ]
            
            all_passed = True
            for endpoint, name in endpoints:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"{name} Endpoint", True, f"{name} endpoint working")
                else:
                    self.log_test(f"{name} Endpoint", False, f"{name} endpoint failed")
                    all_passed = False
            
            return all_passed
        except Exception as e:
            self.log_test("Analytics Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_frontend_accessibility(self):
        """Test frontend accessibility"""
        try:
            # Test if frontend is accessible
            response = requests.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                self.log_test("Frontend Accessibility", True, "Frontend is accessible")
                return True
            else:
                self.log_test("Frontend Accessibility", False, f"Frontend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Accessibility", False, f"Frontend connection failed: {str(e)}")
            return False
    
    def test_api_cors(self):
        """Test CORS configuration"""
        try:
            # Test CORS headers
            response = requests.options(f"{API_BASE_URL}/stats", 
                                      headers={"Origin": "http://localhost:5173"}, 
                                      timeout=10)
            cors_header = response.headers.get('Access-Control-Allow-Origin', '')
            cors_working = cors_header == '*' or 'localhost' in cors_header
            self.log_test("CORS Configuration", cors_working, 
                        f"CORS header: {cors_header}" if cors_working else "CORS not properly configured")
            return cors_working
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Error: {str(e)}")
            return False
    
    def test_performance_benchmarks(self):
        """Test system performance benchmarks"""
        try:
            # Test response times for key endpoints
            endpoints = [
                ("/stats", "Stats"),
                ("/analytics", "Analytics"),
                (f"/vehicles?per_page=10", "Vehicle List")
            ]
            
            performance_results = []
            for endpoint, name in endpoints:
                start_time = time.time()
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                performance_results.append({
                    "endpoint": name,
                    "response_time_ms": response_time,
                    "status_code": response.status_code
                })
            
            avg_response_time = sum(r['response_time_ms'] for r in performance_results) / len(performance_results)
            performance_good = avg_response_time < 1000  # Less than 1 second average
            
            self.log_test("Performance Benchmarks", performance_good, 
                        f"Average response time: {avg_response_time:.1f}ms",
                        {"performance_results": performance_results})
            return performance_good
        except Exception as e:
            self.log_test("Performance Benchmarks", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Pricing Intelligence Platform Integration Tests")
        print("=" * 60)
        
        # Define test suite
        tests = [
            ("API Health", self.test_api_health),
            ("Data Ingestion", self.test_data_ingestion),
            ("Vehicle Matching", self.test_vehicle_matching),
            ("Pricing Scoring", self.test_pricing_scoring),
            ("AI Insights", self.test_ai_insights),
            ("Market Analysis", self.test_market_analysis),
            ("Analytics Endpoints", self.test_analytics_endpoints),
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("CORS Configuration", self.test_api_cors),
            ("Performance Benchmarks", self.test_performance_benchmarks)
        ]
        
        # Run tests
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution failed: {str(e)}")
        
        # Generate summary
        self.generate_test_summary(passed, total)
        
        return passed == total
    
    def generate_test_summary(self, passed, total):
        """Generate test summary report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is fully integrated and working correctly.")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
        
        # Save detailed results
        report = {
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "success_rate": (passed/total)*100,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            },
            "test_results": self.test_results
        }
        
        with open('/home/ubuntu/pricing-intelligence-platform/tests/integration_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: /home/ubuntu/pricing-intelligence-platform/tests/integration_test_report.json")

if __name__ == "__main__":
    # Create tests directory if it doesn't exist
    os.makedirs('/home/ubuntu/pricing-intelligence-platform/tests', exist_ok=True)
    
    # Run tests
    tester = PricingIntelligenceTests()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

