import asyncio
import pytest
from unittest.mock import AsyncMock, patch, mock_open
from fastapi.testclient import TestClient
import json
import sys
import os
from httpx import AsyncClient, ASGITransport

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from app.main import app
from app.modules.director import models
from app.database import engine

client = TestClient(app)

# Mock Data (Simplified for load test)
MOCK_STORY_JSON = json.dumps({"title": "Load Test Story", "scenes": [{"title": "Scene 1", "summary": "Summary"}]})
MOCK_BREAKDOWN_JSON = json.dumps({"shots": [{"shot_id": "1", "type": "Wide", "action": "Action", "camera": "Static", "prompt": "Prompt", "lens": "35mm", "camera_movement": "None", "environment": "Daylight", "lighting": "Natural", "emotion": "Neutral", "color_palette": "Standard", "transition": "Cut"}]})
MOCK_KEYFRAME_JSON = json.dumps({"positive": "Prompt", "style": "Anime"})
MOCK_AUDIO_JSON = json.dumps({"emotion_profile": {}, "tts_prompt": "Text"})
MOCK_SFX_JSON = json.dumps({"sfx_list": [{"name": "sfx", "description": "desc"}]})
MOCK_BGM_JSON = json.dumps({"description": "music"})

async def run_single_episode(i):
    project_id = f"load-test-project-{i}"
    print(f"Starting episode {i}...")
    
    response = client.post("/director/auto/generate-episode", json={
        "project_id": project_id,
        "concept": f"Load Test {i}",
        "style": "Anime",
        "duration": 1
    })
    return response

@pytest.mark.asyncio
async def test_autodirector_load():
    print("\n--- STARTING AUTO-DIRECTOR LOAD TEST (10 Concurrent) ---")
    
    # Patch all external services to avoid rate limits/costs
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
         patch("app.modules.director.model_workers.call_music_gen", new_callable=AsyncMock) as mock_music_gen, \
         patch("builtins.open", mock_open(read_data=b"dummy video data")):

        # Configure Mocks to return valid JSON always
        mock_gemini_auto.return_value = MOCK_STORY_JSON
        mock_gemini_breakdown.return_value = MOCK_BREAKDOWN_JSON
        mock_gemini_keyframe.return_value = MOCK_KEYFRAME_JSON
        mock_gemini_anim.return_value = MOCK_KEYFRAME_JSON
        mock_gemini_audio.return_value = MOCK_AUDIO_JSON
        mock_gemini_sfx.return_value = MOCK_SFX_JSON
        mock_gemini_bgm.return_value = MOCK_BGM_JSON
        
        mock_upload_stream.return_value = {"url": "http://mock/file", "key": "key"}
        mock_upload_public.return_value = {"url": "http://mock/video.mp4", "key": "video.mp4"}
        mock_ffmpeg.return_value = {"status": "success", "output_path": "out.mp4", "temp_dir": "/tmp/mock_dir"}
        mock_sfx_gen.return_value = "http://mock/sfx.wav"
        mock_music_gen.return_value = "http://mock/bgm.wav"

        # Run 10 concurrent requests
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            tasks = []
            for i in range(10):
                tasks.append(ac.post("/director/auto/generate-episode", json={
                    "project_id": f"123e4567-e89b-12d3-a456-42661417400{i}", # Valid UUIDs
                    "concept": f"Load Test {i}",
                    "style": "Anime",
                    "duration": 1
                }))
            
            results = await asyncio.gather(*tasks)
            
            success_count = 0
            for res in results:
                if res.status_code == 200:
                    success_count += 1
                else:
                    print(f"Failed: {res.text}")
            
            print(f"Success: {success_count}/10")
            assert success_count == 10

if __name__ == "__main__":
    asyncio.run(test_autodirector_load())
