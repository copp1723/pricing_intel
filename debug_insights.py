#!/usr/bin/env python3
import requests
import json

API_BASE_URL = "http://localhost:5001/api"
TEST_VIN = "5NPEL4JA2LH042897"

try:
    print("Testing AI insights endpoint...")
    response = requests.get(f"{API_BASE_URL}/vehicle-insights/{TEST_VIN}", timeout=60)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        insights = response.json()
        print(f"Response keys: {list(insights.keys())}")
        
        if 'insights' in insights:
            print(f"insights keys: {list(insights['insights'].keys())}")
            if 'insights' in insights['insights']:
                print(f"insights.insights keys: {list(insights['insights']['insights'].keys())}")
                has_executive_summary = 'executive_summary' in insights['insights']['insights']
                print(f"Has executive_summary: {has_executive_summary}")
                if has_executive_summary:
                    print(f"Executive summary: {insights['insights']['insights']['executive_summary'][:100]}...")
            else:
                print("No 'insights' key in insights")
        else:
            print("No 'insights' key in response")
            
        # Test the exact condition from integration test
        has_insights = 'insights' in insights and 'executive_summary' in insights['insights']
        print(f"Integration test condition result: {has_insights}")
        
        # Correct condition
        correct_condition = ('insights' in insights and 
                           'insights' in insights['insights'] and 
                           'executive_summary' in insights['insights']['insights'])
        print(f"Correct condition result: {correct_condition}")
        
    else:
        print(f"Request failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error: {str(e)}")

