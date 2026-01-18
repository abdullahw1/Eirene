"""Test Yutori API connection"""

import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

YUTORI_API_KEY = os.getenv("YUTORI_API_KEY")
YUTORI_BASE_URL = os.getenv("YUTORI_BASE_URL", "https://api.yutori.com")

print("🔍 Testing Yutori API Connection")
print("=" * 60)
print(f"API Key: {YUTORI_API_KEY[:20]}..." if YUTORI_API_KEY else "No API key found")
print(f"Base URL: {YUTORI_BASE_URL}")
print()

# Test: Create a research task
print("Test: Create Research Task")
print("-" * 60)

url = f"{YUTORI_BASE_URL}/v1/research/tasks"
headers = {
    "X-API-Key": YUTORI_API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "query": "What are the most effective CBT and DBT techniques for treating anxiety? Include evidence-based approaches."
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Yutori API is accessible!")
        data = response.json()
        task_id = data.get('task_id')
        print(f"Task ID: {task_id}")
        print(f"Status: {data.get('status')}")
        print(f"View URL: {data.get('view_url')}")
        
        # Wait a bit and check status
        if task_id:
            print("\nWaiting 5 seconds to check results...")
            time.sleep(5)
            
            status_url = f"{YUTORI_BASE_URL}/v1/research/tasks/{task_id}"
            status_response = requests.get(status_url, headers=headers, timeout=10)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"\nTask Status: {status_data.get('status')}")
                if status_data.get('result'):
                    print(f"Result Preview: {status_data.get('result')[:200]}...")
    else:
        print(f"⚠️  API returned error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error connecting to Yutori: {e}")

print("\n" + "=" * 60)
print("\n✨ Yutori Research API can be used to:")
print("  - Search for therapeutic frameworks")
print("  - Find evidence-based mental health approaches")
print("  - Research current stress signals in communities")
