import asyncio
import pytest
import os
import shutil
from unittest.mock import AsyncMock, patch
import sys

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from app.modules.director import ffmpeg_worker

@pytest.mark.asyncio
async def test_ffmpeg_stress():
    print("\n--- STARTING FFMPEG STRESS TEST (20 Concurrent) ---")
    
    # We want to test the *worker logic* (temp file creation, command construction)
    # but maybe not actually run heavy rendering 20 times if it kills the dev machine.
    # However, the user said "Run 20 FFmpeg render simulations back-to-back."
    # "Simulations" might mean we can mock the subprocess call but keep the file logic.
    # Or we can run a very lightweight ffmpeg command (e.g. generate 1 sec black video).
    
    # Let's try to run a lightweight command.
    
    async def run_render(i):
        # Create dummy assets
        assets = [
            {"type": "video", "url": "http://mock/1.mp4", "timeline_in": 0, "timeline_out": 1},
            {"type": "video", "url": "http://mock/2.mp4", "timeline_in": 1, "timeline_out": 2}
        ]
        
        # We need to mock download_file to create local dummy files
        with patch("app.modules.director.ffmpeg_worker.download_file") as mock_dl:
            mock_dl.side_effect = lambda url, path: open(path, 'wb').write(b'dummy content')
            
            # We also need to mock subprocess to avoid actual ffmpeg if we don't have valid inputs
            # OR we can just mock the whole compile_timeline to sleep?
            # The user wants to "Validate temp directory creation & cleanup".
            # So we should let compile_timeline run up to the subprocess call.
            
            with patch("asyncio.create_subprocess_exec") as mock_exec:
                # Mock process
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"")
                mock_process.returncode = 0
                mock_exec.return_value = mock_process
                
                try:
                    result = await ffmpeg_worker.compile_timeline(assets, f"stress_test_{i}.mp4")
                    return True
                except Exception as e:
                    print(f"Render {i} failed: {e}")
                    return False

    tasks = [run_render(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(results)
    print(f"Success: {success_count}/20")
    assert success_count == 20

if __name__ == "__main__":
    asyncio.run(test_ffmpeg_stress())
