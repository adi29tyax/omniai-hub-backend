import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from app.modules.ide import utils

@pytest.mark.asyncio
async def test_ai_worker_stress():
    print("\n--- STARTING AI WORKER STRESS TEST (100 Concurrent) ---")
    
    # Mock httpx to simulate latency
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Mock AI Response"}]}}]
        }
        
        # Simulate delay
        async def delayed_response(*args, **kwargs):
            await asyncio.sleep(0.1)
            return mock_response
            
        mock_post.side_effect = delayed_response
        
        async def run_query(i):
            try:
                # We need to set a dummy key to bypass the placeholder check
                with patch("app.modules.ide.utils.GEMINI_API_KEY", "dummy_key"):
                    response = await utils.call_gemini(f"Test prompt {i}")
                    return response == "Mock AI Response"
            except Exception as e:
                print(f"Query {i} failed: {e}")
                return False

        tasks = [run_query(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(results)
        print(f"Success: {success_count}/100")
        assert success_count == 100

if __name__ == "__main__":
    asyncio.run(test_ai_worker_stress())
