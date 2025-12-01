import asyncio
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from app.storage import r2

@pytest.mark.asyncio
async def test_r2_upload_stress():
    print("\n--- STARTING R2 UPLOAD STRESS TEST (50 Concurrent) ---")
    
    # Mock the boto3 client inside r2.py
    with patch("app.storage.r2.get_r2_client") as mock_get_client:
        mock_s3 = MagicMock()
        mock_get_client.return_value = mock_s3
        
        async def run_upload(i):
            file_content = b"x" * 1024 # 1KB dummy file
            filename = f"stress_test_{i}.bin"
            
            try:
                # We are testing the wrapper logic (retry, error handling)
                # We simulate random failures if we want, but for now let's test concurrency
                result = r2.upload_stream_to_r2(filename, file_content)
                return result["url"] is not None
            except Exception as e:
                print(f"Upload {i} failed: {e}")
                return False

        tasks = [run_upload(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(results)
        print(f"Success: {success_count}/50")
        assert success_count == 50

if __name__ == "__main__":
    asyncio.run(test_r2_upload_stress())
