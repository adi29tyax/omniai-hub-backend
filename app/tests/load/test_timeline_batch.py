import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, mock_open
import sys
import os
import uuid

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from app.modules.director import timeline_service, schemas

@pytest.mark.asyncio
async def test_timeline_batch():
    print("\n--- STARTING TIMELINE BATCH TEST (30 Concurrent) ---")
    
    # Mock ffmpeg and R2
    with patch("app.modules.director.ffmpeg_worker.compile_timeline", new_callable=AsyncMock) as mock_ffmpeg, \
         patch("app.modules.director.timeline_service.upload_public") as mock_upload, \
         patch("builtins.open", mock_open(read_data=b"dummy video data")):
        
        mock_ffmpeg.return_value = {"status": "success", "output_path": "out.mp4", "temp_dir": "/tmp/mock_dir"}
        mock_upload.return_value = {"url": "http://mock/video.mp4", "key": "video.mp4"}
        
        async def run_timeline_build(i):
            # Create a dummy request
            request = schemas.TimelineRequest(
                project_id=f"123e4567-e89b-12d3-a456-4266141740{i:02d}", # Valid UUID-like
                episode_title=f"Timeline Test {i}",
                layers=[],
                scene_order=[]
            )
            
            # We need a mock DB session
            mock_db = MagicMock()
            
            # Mock db.refresh to set an ID
            def mock_refresh(obj):
                obj.id = uuid.uuid4()
            mock_db.refresh.side_effect = mock_refresh
            
            try:
                # We are testing the service logic orchestration
                result = await timeline_service.compile_episode(mock_db, request)
                return result.url is not None
            except Exception as e:
                print(f"Timeline {i} failed: {e}")
                return False

        tasks = [run_timeline_build(i) for i in range(30)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(results)
        print(f"Success: {success_count}/30")
        assert success_count == 30

if __name__ == "__main__":
    asyncio.run(test_timeline_batch())
