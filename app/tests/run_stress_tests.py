import asyncio
import sys
import os
import json
import time

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(os.path.join(os.path.dirname(__file__), "load"))

from monitor import ResourceMonitor

async def run_tests():
    print("--- STARTING PHASE 9.4 LOAD & STRESS TESTS ---")
    
    # Start Monitor
    monitor = ResourceMonitor(interval=0.5)
    monitor.start()
    
    results = {}
    
    try:
        # 1. Auto-Director Load
        print("\n[1/5] Running Auto-Director Load Test...")
        start = time.time()
        ret = os.system("python -m pytest app/tests/load/test_autodirector_load.py")
        results["autodirector"] = "PASS" if ret == 0 else "FAIL"
        print(f"Time: {time.time() - start:.2f}s")
        
        # 2. FFmpeg Stress
        print("\n[2/5] Running FFmpeg Stress Test...")
        start = time.time()
        ret = os.system("python -m pytest app/tests/load/test_ffmpeg_stress.py")
        results["ffmpeg"] = "PASS" if ret == 0 else "FAIL"
        print(f"Time: {time.time() - start:.2f}s")
        
        # 3. R2 Upload Stress
        print("\n[3/5] Running R2 Upload Stress Test...")
        start = time.time()
        ret = os.system("python -m pytest app/tests/load/test_r2_upload_stress.py")
        results["r2_upload"] = "PASS" if ret == 0 else "FAIL"
        print(f"Time: {time.time() - start:.2f}s")
        
        # 4. Timeline Batch
        print("\n[4/5] Running Timeline Batch Test...")
        start = time.time()
        ret = os.system("python -m pytest app/tests/load/test_timeline_batch.py")
        results["timeline"] = "PASS" if ret == 0 else "FAIL"
        print(f"Time: {time.time() - start:.2f}s")
        
        # 5. AI Worker Stress
        print("\n[5/5] Running AI Worker Stress Test...")
        start = time.time()
        ret = os.system("python -m pytest app/tests/load/test_ai_worker_stress.py")
        results["ai_worker"] = "PASS" if ret == 0 else "FAIL"
        print(f"Time: {time.time() - start:.2f}s")
        
    finally:
        monitor.stop()
        
    # Generate Report
    summary = monitor.get_summary()
    report = {
        "results": results,
        "resources": summary
    }
    
    report_path = "/tmp/omnistudio/load_test_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print("\n--- PHASE 9.4 LOAD & STRESS TEST COMPLETE ---")
    print("\nSummary:")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(run_tests())
