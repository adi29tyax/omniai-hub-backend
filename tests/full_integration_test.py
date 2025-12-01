import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.modules.director import models
from app.database import get_db, engine

# Create Tables
models.Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Mock Data
MOCK_STORY_JSON = json.dumps({
    "title": "Test Story",
    "logline": "A test story logline",
    "theme": "Testing",
    "characters": [
        {"name": "Hero", "role": "Protagonist", "description": "A brave tester", "visual_style": "Anime", "voice_type": "Heroic"}
    ],
    "scenes": [
        {"title": "Scene 1", "summary": "Hero starts testing", "location": "Lab", "time_of_day": "Day"}
    ]
})

MOCK_BREAKDOWN_JSON = json.dumps({
    "shots": [
        {
            "shot_id": "1",
            "type": "Wide",
            "lens": "35mm",
            "camera_movement": "Static",
            "environment": "Lab",
            "lighting": "Cinematic",
            "action": "Hero types",
            "emotion": "Focused",
            "color_palette": "Blue",
            "transition": "Cut",
            "prompt": "Wide shot of lab, hero typing",
            "description": "Wide shot of lab", 
            "camera": "Wide", 
            "duration": 2
        },
        {
            "shot_id": "2",
            "type": "Close Up",
            "lens": "85mm",
            "camera_movement": "Pan",
            "environment": "Lab",
            "lighting": "Soft",
            "action": "Code scrolls",
            "emotion": "Intense",
            "color_palette": "Green",
            "transition": "Fade",
            "prompt": "Close up of screen code",
            "description": "Close up of screen", 
            "camera": "Close Up", 
            "duration": 2
        }
    ]
})

MOCK_KEYFRAME_JSON = json.dumps({
    "positive": "Anime style lab, wide shot",
    "negative": "bad quality",
    "style": "Anime"
})

MOCK_AUDIO_JSON = json.dumps({
    "emotion_profile": {"happiness": 0.5},
    "tts_prompt": "Hello world"
})

MOCK_SFX_JSON = json.dumps({
    "sfx_list": [{"name": "typing", "description": "Keyboard typing sound"}]
})

MOCK_BGM_JSON = json.dumps({
    "description": "Upbeat electronic music"
})

@pytest.mark.asyncio
async def test_full_integration():
    print("\n--- STARTING PHASE 9.3 FULL INTEGRATION TEST ---")
    
    # Mock External Services
    # Patch all services that use call_gemini
    with patch("app.modules.director.auto_director_service.call_gemini", new_callable=AsyncMock) as mock_gemini_auto, \
         patch("app.modules.director.breakdown_service.call_gemini", new_callable=AsyncMock) as mock_gemini_breakdown, \
         patch("app.modules.director.keyframe_service.call_gemini", new_callable=AsyncMock) as mock_gemini_keyframe, \
         patch("app.modules.director.animation_service.call_gemini", new_callable=AsyncMock) as mock_gemini_anim, \
         patch("app.modules.director.audio_service.call_gemini", new_callable=AsyncMock) as mock_gemini_audio, \
         patch("app.modules.director.sound_designer.call_gemini", new_callable=AsyncMock) as mock_gemini_sfx, \
         patch("app.modules.director.music_generator.call_gemini", new_callable=AsyncMock) as mock_gemini_bgm, \
         patch("app.storage.r2.upload_stream_to_r2") as mock_upload_stream, \
         patch("app.modules.director.timeline_service.upload_public") as mock_upload_public, \
         patch("app.modules.director.ffmpeg_worker.compile_timeline", new_callable=AsyncMock) as mock_ffmpeg, \
         patch("app.modules.director.model_workers.call_sfx_gen", new_callable=AsyncMock) as mock_sfx_gen, \
         patch("app.modules.director.model_workers.call_music_gen", new_callable=AsyncMock) as mock_music_gen:
        
        # Setup Mocks
        # Story
        mock_gemini_auto.side_effect = [MOCK_STORY_JSON]
        
        # Breakdown (2 calls: 1. Generate, 2. Fix)
        mock_gemini_breakdown.side_effect = [MOCK_BREAKDOWN_JSON, MOCK_BREAKDOWN_JSON]
        
        # Keyframe (2 shots * 2 calls each = 4)
        mock_gemini_keyframe.side_effect = [MOCK_KEYFRAME_JSON] * 4
        
        # Animation (2 shots * 2 calls each = 4)
        mock_gemini_anim.side_effect = [MOCK_KEYFRAME_JSON] * 4
        
        # Audio Voice (2 shots)
        mock_gemini_audio.side_effect = [MOCK_AUDIO_JSON, MOCK_AUDIO_JSON]
        
        # SFX (2 shots)
        mock_gemini_sfx.side_effect = [MOCK_SFX_JSON, MOCK_SFX_JSON]
        
        # BGM (1 scene)
        mock_gemini_bgm.side_effect = [MOCK_BGM_JSON]
        
        mock_upload_stream.return_value = {"url": "https://cdn.omniai.app/test.png", "key": "test.png"}
        mock_upload_public.return_value = {"url": "https://cdn.omniai.app/test.mp4", "key": "test.mp4"}
        mock_ffmpeg.return_value = {
            "status": "success",
            "output_path": "test_output.mp4",
            "temp_dir": "/tmp",
            "duration": 10.0,
            "log": []
        }
        
        # Create dummy file for upload
        with open("test_output.mp4", "wb") as f:
            f.write(b"fake video content")
        mock_sfx_gen.return_value = "https://cdn.omniai.app/sfx.wav"
        mock_music_gen.return_value = "https://cdn.omniai.app/bgm.wav"
        
        # Client
        client = TestClient(app)
        
        # 1. Story Engine Test
        print("\n1. Testing Story Engine...")
        project_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.post("/director/auto/generate-story", json={
            "project_id": project_id,
            "concept": "Integration Test Story",
            "style": "Anime",
            "duration": 1
        })
        
        if response.status_code != 200:
            print(f"   FAILED. Status: {response.status_code}")
            print(f"   Response: {response.text}")
        else:
            story_data = response.json()
            print(f"   PASSED. Story ID: {story_data['id']}")

        # 10. Auto-Director Full Test (This covers steps 2-9 implicitly via the service orchestration)
        print("\n10. Testing Auto-Director (Full Pipeline)...")
        # Reset mocks
        mock_gemini_auto.reset_mock()
        mock_gemini_breakdown.reset_mock()
        mock_gemini_keyframe.reset_mock()
        mock_gemini_anim.reset_mock()
        mock_gemini_audio.reset_mock()
        mock_gemini_sfx.reset_mock()
        mock_gemini_bgm.reset_mock()
        
        mock_gemini_auto.side_effect = [MOCK_STORY_JSON]
        mock_gemini_breakdown.side_effect = [MOCK_BREAKDOWN_JSON, MOCK_BREAKDOWN_JSON]
        mock_gemini_keyframe.side_effect = [MOCK_KEYFRAME_JSON] * 4
        mock_gemini_anim.side_effect = [MOCK_KEYFRAME_JSON] * 4
        mock_gemini_audio.side_effect = [MOCK_AUDIO_JSON, MOCK_AUDIO_JSON]
        mock_gemini_sfx.side_effect = [MOCK_SFX_JSON, MOCK_SFX_JSON]
        mock_gemini_bgm.side_effect = [MOCK_BGM_JSON]
        
        response = client.post("/director/auto/generate-episode", json={
            "project_id": project_id,
            "concept": "Auto Director Test",
            "style": "Epic",
            "duration": 1
        })
        
        if response.status_code != 200:
            print(f"   FAILED. Status: {response.status_code}")
            print(f"   Response: {response.text}")
        else:
            data = response.json()
            print(f"   PASSED. Episode URL: {data['episode_url']}")
            print(f"   Logs: {len(data['logs'])} entries")
            
    print("\n--- PHASE 9.3 INTEGRATION TEST COMPLETE ---")

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(test_full_integration())
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"TEST ERROR: {e}")
        sys.exit(1)
