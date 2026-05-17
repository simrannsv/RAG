"""
Simple test to query GraphRAG with diagnostic questions
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import time

BASE_URL = "http://localhost:8000"
GRAPH_NAME = "IPL"
USERNAME = "tigergraph"
PASSWORD = "tigergraph"

test_questions = [
    "What entities are in the graph?",
    "Tell me about players in the graph",
    "List all teams",
    "How many players are there?",
    "Which players have represented more than 5 different IPL teams?",
]

print("\n" + "="*70)
print("GRAPHRAG DIAGNOSTIC TEST")
print("="*70)

for i, q in enumerate(test_questions, 1):
    print(f"\n[{i}] Question: {q}")
    print("-"*70)
    
    try:
        url = f"{BASE_URL}/ui/{GRAPH_NAME}/query"
        resp = requests.get(
            url,
            params={"q": q, "rag_pattern": "hybridsearch"},
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=60,
        )
        
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            payload = resp.json()
            print(f"Response Type: {type(payload)}")
            
            if isinstance(payload, str):
                payload = json.loads(payload) if payload.startswith('{') else {"content": payload}
            
            if isinstance(payload, dict):
                print(f"Content: {str(payload.get('content', payload))[:300]}")
                print(f"Answered: {payload.get('answered_question')}")
                print(f"Response Type: {payload.get('response_type')}")
            else:
                print(f"Content: {str(payload)[:300]}")
        else:
            print(f"Error: {resp.text[:300]}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - service is slow or unresponsive")
    except Exception as e:
        print(f"❌ Error: {str(e)[:200]}")
    
    time.sleep(2)

print("\n" + "="*70)
print("DIAGNOSTIC TEST COMPLETE")
print("="*70 + "\n")
