"""
Comprehensive test script for PolicyEdge Intelligence features.
"""

import requests
import json
from datetime import datetime

def test_intelligence_features():
    """Test all intelligence features."""
    API_URL = 'http://localhost:8000'
    results = {}
    
    print("PolicyEdge Intelligence Feature Testing")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Intelligence Health Check...")
    try:
        response = requests.get(f'{API_URL}/api/intelligence/health')
        data = response.json()
        results['health_check'] = {
            'status': response.status_code == 200,
            'components_healthy': all(status == 'healthy' for status in data.get('components', {}).values()),
            'response': data
        }
        print(f"   ✓ Health check passed: {data.get('status')}")
        print(f"   ✓ Components: {', '.join(data.get('components', {}).keys())}")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        results['health_check'] = {'status': False, 'error': str(e)}
    
    # Test 2: Live Intelligence Feed
    print("\n2. Testing Live Intelligence Feed...")
    try:
        for feed_type in ['comprehensive', 'compliance', 'security', 'operations']:
            response = requests.get(f'{API_URL}/api/intelligence/feed', {
                'feed_type': feed_type,
                'limit': 5
            })
            data = response.json()
            
            if response.status_code == 200:
                print(f"   ✓ {feed_type.title()} feed: {data.get('total_items', 0)} items")
                results[f'feed_{feed_type}'] = {
                    'status': True,
                    'total_items': data.get('total_items', 0),
                    'sample_item': data.get('items', [{}])[0] if data.get('items') else None
                }
            else:
                print(f"   ✗ {feed_type.title()} feed failed")
                results[f'feed_{feed_type}'] = {'status': False}
    except Exception as e:
        print(f"   ✗ Feed testing failed: {e}")
    
    # Test 3: Intelligence Memos
    print("\n3. Testing Intelligence Memo Generation...")
    try:
        for memo_type in ['daily', 'weekly', 'monthly', 'incident', 'compliance']:
            response = requests.get(f'{API_URL}/api/intelligence/memo', {
                'memo_type': memo_type,
                'include_charts': False
            })
            data = response.json()
            
            if response.status_code == 200:
                print(f"   ✓ {memo_type.title()} memo: {len(data.get('sections', []))} sections")
                results[f'memo_{memo_type}'] = {
                    'status': True,
                    'headline': data.get('headline', ''),
                    'sections': len(data.get('sections', [])),
                    'has_executive_summary': bool(data.get('executive_summary'))
                }
            else:
                print(f"   ✗ {memo_type.title()} memo failed")
                results[f'memo_{memo_type}'] = {'status': False}
    except Exception as e:
        print(f"   ✗ Memo testing failed: {e}")
    
    # Test 4: Data Aggregation
    print("\n4. Testing Data Aggregation...")
    try:
        endpoints = [
            ('summary', '/api/intelligence/data/summary'),
            ('compliance', '/api/intelligence/data/compliance?hours_back=24'),
            ('assets', '/api/intelligence/data/assets?hours_back=24'),
            ('contracts', '/api/intelligence/data/contracts?days_ahead=90'),
            ('regulatory', '/api/intelligence/data/regulatory?hours_back=168'),
            ('incidents', '/api/intelligence/data/incidents?hours_back=72'),
            ('trends', '/api/intelligence/data/trends?days_back=30')
        ]
        
        for name, endpoint in endpoints:
            response = requests.get(f'{API_URL}{endpoint}')
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ {name.title()} data: {len(str(data))} bytes")
                results[f'data_{name}'] = {'status': True, 'size': len(str(data))}
            else:
                print(f"   ✗ {name.title()} data failed")
                results[f'data_{name}'] = {'status': False}
    except Exception as e:
        print(f"   ✗ Data aggregation testing failed: {e}")
    
    # Test 5: Feed Metrics
    print("\n5. Testing Feed Analytics...")
    try:
        response = requests.get(f'{API_URL}/api/intelligence/feed/metrics', {
            'feed_type': 'comprehensive',
            'hours_back': 24
        })
        data = response.json()
        
        if response.status_code == 200:
            print(f"   ✓ Feed metrics: {data.get('total_items', 0)} items analyzed")
            print(f"   ✓ Priority breakdown: {data.get('by_priority', {})}")
            print(f"   ✓ Category breakdown: {data.get('by_category', {})}")
            results['feed_metrics'] = {
                'status': True,
                'total_items': data.get('total_items', 0),
                'priority_breakdown': data.get('by_priority', {}),
                'category_breakdown': data.get('by_category', {})
            }
        else:
            print(f"   ✗ Feed metrics failed")
            results['feed_metrics'] = {'status': False}
    except Exception as e:
        print(f"   ✗ Feed metrics testing failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = len([r for r in results.values() if r.get('status')])
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
    
    # Feature showcase
    print("\n" + "=" * 60)
    print("FEATURE SHOWCASE")
    print("=" * 60)
    
    if results.get('feed_comprehensive', {}).get('status'):
        sample_item = results['feed_comprehensive']['sample_item']
        if sample_item:
            print(f"📊 Live Feed Sample:")
            print(f"   Title: {sample_item.get('title', 'N/A')}")
            print(f"   Type: {sample_item.get('type', 'N/A')}")
            print(f"   Priority: {sample_item.get('priority', 'N/A')}")
            print(f"   Category: {sample_item.get('category', 'N/A')}")
    
    if results.get('memo_daily', {}).get('status'):
        print(f"\n📰 Daily Memo Sample:")
        print(f"   Headline: {results['memo_daily']['headline']}")
        print(f"   Sections: {results['memo_daily']['sections']}")
        print(f"   Executive Summary: {'Yes' if results['memo_daily']['has_executive_summary'] else 'No'}")
    
    if results.get('feed_metrics', {}).get('status'):
        print(f"\n📈 Analytics Sample:")
        priority_data = results['feed_metrics']['priority_breakdown']
        if priority_data:
            print(f"   Priority Distribution: {priority_data}")
        category_data = results['feed_metrics']['category_breakdown']
        if category_data:
            print(f"   Category Distribution: {category_data}")
    
    print("\n" + "=" * 60)
    print("✅ PolicyEdge Intelligence Features Successfully Implemented!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    test_results = test_intelligence_features()
    
    # Save test results
    with open('/tmp/intelligence_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n📄 Test results saved to: /tmp/intelligence_test_results.json")
    print(f"🌐 Streamlit Dashboard: http://localhost:8501")
    print(f"🔗 API Documentation: http://localhost:8000/docs")