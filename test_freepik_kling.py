"""Test Freepik Kling 2.6 API connection"""

import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")
BASE_URL = "https://api.freepik.com/v1/ai/image-to-video"

print("🎬 Testing Freepik Kling 2.6 API Connection")
print("=" * 80)
print(f"API Key: {FREEPIK_API_KEY[:20]}..." if FREEPIK_API_KEY else "No API key found")
print()

# Test 1: Get status of all tasks (to verify API key works)
print("Test 1: Get All Tasks Status")
print("-" * 80)

url = f"{BASE_URL}/kling-v2-6"
headers = {
    "x-freepik-api-key": FREEPIK_API_KEY
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Freepik Kling API is accessible!")
        data = response.json()
        print(f"Response: {data}")
        
        if "tasks" in data:
            print(f"\nExisting tasks: {len(data.get('tasks', []))}")
            for task in data.get('tasks', [])[:3]:  # Show first 3 tasks
                print(f"  - Task ID: {task.get('task_id')}")
                print(f"    Status: {task.get('status')}")
                if task.get('video_url'):
                    print(f"    Video URL: {task.get('video_url')[:50]}...")
    else:
        print(f"⚠️  API returned error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error connecting to Freepik: {e}")

print("\n" + "=" * 80)

# Test 2: Create a test video (optional - costs credits)
print("\nTest 2: Create Test Video (Optional)")
print("-" * 80)
print("⚠️  This will use API credits. Uncomment to test video generation.")
print()

# Uncomment below to test video generation:
"""
url = f"{BASE_URL}/kling-v2-6-pro"
headers = {
    "Content-Type": "application/json",
    "x-freepik-api-key": FREEPIK_API_KEY
}
payload = {
    "prompt": "Gentle waves flowing on a peaceful beach at sunset, calm and therapeutic",
    "duration": "5",
    "cfg_scale": 0.5,
    "aspect_ratio": "widescreen_16_9",
    "generate_audio": False
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201, 202]:
        print("✅ Video generation task created!")
        data = response.json()
        print(f"Task ID: {data.get('task_id')}")
        print(f"Status: {data.get('status')}")
        print(f"\nNote: Video generation takes 2-5 minutes.")
        print(f"Check status with: GET {BASE_URL}/kling-v2-6")
    else:
        print(f"⚠️  API returned error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error creating video: {e}")
"""

print("\n" + "=" * 80)
print("\n✨ Freepik Kling 2.6 API can be used to:")
print("  - Generate AI videos from text prompts")
print("  - Create 5 or 10 second video clips")
print("  - Perfect for 'Mindful Moment' therapeutic videos")
print("  - Combine with ElevenLabs audio for complete interventions")
print()
print("📝 Next Steps:")
print("  1. Implement FreepikKlingClient in Generation Agent")
print("  2. Use therapeutic prompts from StrategyAgent")
print("  3. Poll for completion and download videos")
print("  4. Combine with ElevenLabs audio using ffmpeg")
