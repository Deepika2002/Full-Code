#!/usr/bin/env python3
"""
Test script for ImpactAnalyzer Backend Services
"""

import requests
import json
import time
from datetime import datetime

# Service URLs
SERVICES = {
    "MS-Index": "http://localhost:8001",
    "MS-MR": "http://localhost:8002", 
    "MS-Common": "http://localhost:8003",
    "MS-AI": "http://localhost:8004"
}

# API Key for testing
API_KEY = "dev-key-123"
HEADERS = {
    "Content-Type": "application/json",
    "X-Impact-Analyzer-Api-Key": API_KEY
}

def test_health_endpoints():
    """Test health endpoints for all services"""
    print("🏥 Testing Health Endpoints")
    print("-" * 30)
    
    health_endpoints = {
        "MS-Index": "/index/health",
        "MS-MR": "/mr/health",
        "MS-Common": "/common/health", 
        "MS-AI": "/ai/health"
    }
    
    for service, endpoint in health_endpoints.items():
        try:
            url = SERVICES[service] + endpoint
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {service}: {response.json()}")
            else:
                print(f"❌ {service}: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {service}: Connection failed - {e}")

def test_dependency_graph_ingestion():
    """Test dependency graph ingestion"""
    print("\n📊 Testing Dependency Graph Ingestion")
    print("-" * 40)
    
    # Sample dependency graph data
    sample_graph = {
        "projectId": "angular-springboot-ecommerce",
        "repoUrl": "https://github.com/sinnedpenguin/angular-springboot-ecommerce.git",
        "commitHash": "main",
        "timestamp": datetime.now().isoformat() + "Z",
        "author": "test-user",
        "dependencyGraph": {
            "nodes": [
                {"id": "UserService", "name": "UserService", "type": "class"},
                {"id": "PaymentController", "name": "PaymentController", "type": "class"},
                {"id": "OrderEntity", "name": "OrderEntity", "type": "class"}
            ],
            "edges": [
                {"from_node": "UserService", "to": "PaymentController", "type": "depends-on"},
                {"from_node": "PaymentController", "to": "OrderEntity", "type": "uses"}
            ]
        }
    }
    
    try:
        url = SERVICES["MS-Index"] + "/index/ingest-graph"
        response = requests.post(url, json=sample_graph, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Graph ingestion successful:")
            print(f"   Index ID: {result.get('indexId', 'N/A')}")
            print(f"   Vector Store: {result.get('vectorStorePath', 'N/A')}")
            return result.get('indexId')
        else:
            print(f"❌ Graph ingestion failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Graph ingestion failed: {e}")
    
    return None

def test_mr_analysis():
    """Test MR analysis"""
    print("\n🔍 Testing MR Analysis")
    print("-" * 25)
    
    # Sample MR data
    sample_mr = {
        "projectId": "angular-springboot-ecommerce",
        "mrId": "MR-TEST-001",
        "author": "test-user",
        "timestamp": datetime.now().isoformat() + "Z",
        "gitDiff": """diff --git a/src/main/java/com/ecommerce/service/UserService.java b/src/main/java/com/ecommerce/service/UserService.java
index 1234567..abcdefg 100644
--- a/src/main/java/com/ecommerce/service/UserService.java
+++ b/src/main/java/com/ecommerce/service/UserService.java
@@ -45,6 +45,12 @@ public class UserService {
     }
 
     public User createUser(UserDto userDto) {
+        // Add email validation
+        if (!isValidEmail(userDto.getEmail())) {
+            throw new InvalidEmailException("Invalid email format");
+        }
+        
+        // Encrypt password before saving
         User user = new User();
         user.setEmail(userDto.getEmail());
-        user.setPassword(userDto.getPassword());
+        user.setPassword(encryptPassword(userDto.getPassword()));
         return userRepository.save(user);
     }""",
        "changedFiles": [
            {"path": "src/main/java/com/ecommerce/service/UserService.java", "type": "MODIFY"}
        ],
        "repositoryInfo": {
            "repoUrl": "https://github.com/sinnedpenguin/angular-springboot-ecommerce.git",
            "branch": "main",
            "commitHash": "abcdefg"
        }
    }
    
    try:
        url = SERVICES["MS-MR"] + "/mr/analyze"
        response = requests.post(url, json=sample_mr, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ MR analysis successful:")
            print(f"   Analysis ID: {result.get('analysisId', 'N/A')}")
            print(f"   Severity Score: {result.get('mrSummary', {}).get('severityScore', 'N/A')}")
            print(f"   Affected Classes: {result.get('mrSummary', {}).get('affectedClassesCount', 'N/A')}")
            return result.get('analysisId')
        else:
            print(f"❌ MR analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ MR analysis failed: {e}")
    
    return None

def test_common_endpoints():
    """Test common service endpoints"""
    print("\n📈 Testing Common Service Endpoints")
    print("-" * 35)
    
    endpoints = [
        "/stats/yesterday",
        "/stats/current", 
        "/impact-map",
        "/test-flows"
    ]
    
    for endpoint in endpoints:
        try:
            url = SERVICES["MS-Common"] + endpoint
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {endpoint}: Success")
                if 'stats' in result:
                    stats = result['stats']
                    print(f"   Sample data: {list(stats.keys())[:3]}")
                elif 'testFlows' in result:
                    flows = result['testFlows']
                    print(f"   Test flows count: {len(flows)}")
                elif 'impactMap' in result:
                    impact = result['impactMap']
                    print(f"   Impact entries: {len(impact)}")
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: {e}")

def test_ai_service():
    """Test AI service"""
    print("\n🤖 Testing AI Service")
    print("-" * 20)
    
    # Sample impact analysis request
    sample_request = {
        "mrId": "MR-TEST-001",
        "changedClasses": ["UserService", "PaymentController"],
        "codeContext": "Modified user service to add email validation and password encryption",
        "vectorContext": None
    }
    
    try:
        url = SERVICES["MS-AI"] + "/analysis/impact"
        response = requests.post(url, json=sample_request, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('analysis', {})
            print(f"✅ AI analysis successful:")
            print(f"   Severity Score: {analysis.get('severityScore', 'N/A')}")
            print(f"   Code Coverage: {analysis.get('codeCoverage', 'N/A')}%")
            print(f"   Affected Classes: {len(analysis.get('affectedClasses', []))}")
            print(f"   Test Flows: {len(analysis.get('testFlows', []))}")
        else:
            print(f"❌ AI analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ AI analysis failed: {e}")

def main():
    """Main test function"""
    print("🧪 ImpactAnalyzer Backend Services Test Suite")
    print("=" * 50)
    
    # Wait for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(3)
    
    # Run tests
    test_health_endpoints()
    test_dependency_graph_ingestion()
    test_mr_analysis()
    test_common_endpoints()
    test_ai_service()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\nNote: Some tests may fail if services are not running or")
    print("if external dependencies (MySQL, OpenAI API) are not configured.")

if __name__ == "__main__":
    main()