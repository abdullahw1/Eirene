"""Test instant playback feature"""
import requests
import json

def test_instant_playback():
    """Test that instant playback returns a video"""
    url = "http://localhost:5001/api/instant-playback"
    
    # Test different communities
    communities = ["r/anxiety", "r/burnout", "r/depression", "r/lonely"]
    
    for community in communities:
        print(f"\n🧪 Testing instant playback for {community}...")
        
        response = requests.post(
            url,
            json={"community": community},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify response structure
        assert data["success"] == True, "Response should be successful"
        assert data["instant_playback"] == True, "Should be instant playback mode"
        assert "video_url" in data, "Should have video_url"
        assert "monitor_output" in data, "Should have monitor_output"
        assert "strategy_output" in data, "Should have strategy_output"
        assert "generation_output" in data, "Should have generation_output"
        
        # Verify monitor output
        assert data["monitor_output"]["community"] == community
        assert 0 <= data["monitor_output"]["severity"] <= 1
        
        # Verify strategy output
        assert data["strategy_output"]["framework"] in ["CBT", "DBT"]
        assert len(data["strategy_output"]["techniques"]) > 0
        
        # Verify generation output
        assert data["generation_output"]["video_duration"] > 0
        assert len(data["generation_output"]["script"]) > 0
        
        print(f"✅ {community}: Success!")
        print(f"   Video: {data['video_url']}")
        print(f"   Framework: {data['strategy_output']['framework']}")
        print(f"   Theme: {data['strategy_output']['content_theme']}")
        print(f"   Duration: {data['generation_output']['video_duration']}s")
        
        # Test video file is accessible
        video_url = f"http://localhost:5001{data['video_url']}"
        video_response = requests.head(video_url)
        assert video_response.status_code == 200, f"Video should be accessible: {video_url}"
        print(f"   ✅ Video file accessible")

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 Testing Instant Playback Feature")
    print("=" * 60)
    
    try:
        test_instant_playback()
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
