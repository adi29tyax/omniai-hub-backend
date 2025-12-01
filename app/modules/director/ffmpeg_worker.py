import asyncio
import os
import uuid
import shutil
import logging
import aiohttp

logger = logging.getLogger(__name__)

async def download_file(session, url, path):
    async with session.get(url) as resp:
        if resp.status == 200:
            with open(path, 'wb') as f:
                f.write(await resp.read())
            return path
    return None

async def compile_timeline(scene_assets, output_filename):
    logs = []
    temp_id = str(uuid.uuid4())
    temp_dir = os.path.join("/tmp/omnistudio", temp_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        logs.append(f"Created temp dir: {temp_dir}")
        
        video_inputs = []
        audio_inputs = []
        
        # 1. Download Assets
        async with aiohttp.ClientSession() as session:
            for scene in scene_assets:
                # Download Animations
                for i, url in enumerate(scene.get("animations", [])):
                    path = os.path.join(temp_dir, f"scene_{scene['scene_id']}_anim_{i}.mp4")
                    if await download_file(session, url, path):
                        video_inputs.append(path)
                        
                # Download Audio (Voice + SFX + BGM) - Simplified mixing
                for i, url in enumerate(scene.get("voices", [])):
                    path = os.path.join(temp_dir, f"scene_{scene['scene_id']}_voice_{i}.mp3")
                    if await download_file(session, url, path):
                        audio_inputs.append(path)
                        
                for i, url in enumerate(scene.get("sfx", [])):
                    path = os.path.join(temp_dir, f"scene_{scene['scene_id']}_sfx_{i}.mp3")
                    if await download_file(session, url, path):
                        audio_inputs.append(path)
                        
                for i, url in enumerate(scene.get("bgm", [])):
                    path = os.path.join(temp_dir, f"scene_{scene['scene_id']}_bgm_{i}.mp3")
                    if await download_file(session, url, path):
                        audio_inputs.append(path)

        # 2. Build FFmpeg Command
        cmd = ["ffmpeg", "-y"]
        
        # Add inputs
        for v in video_inputs:
            cmd.extend(["-i", v])
            
        for a in audio_inputs:
            cmd.extend(["-i", a])
            
        # Filter Complex
        num_videos = len(video_inputs)
        num_audios = len(audio_inputs)
        
        fc_parts = []
        
        # Video Concat
        if num_videos > 0:
            v_streams = "".join([f"[{i}:v]" for i in range(num_videos)])
            fc_parts.append(f"{v_streams}concat=n={num_videos}:v=1:a=0[outv]")
        
        # Audio Mix
        if num_audios > 0:
            a_streams = "".join([f"[{i+num_videos}:a]" for i in range(num_audios)])
            fc_parts.append(f"{a_streams}amix=inputs={num_audios}:duration=longest[outa]")
        
        if num_videos > 0 or num_audios > 0:
            cmd.append("-filter_complex")
            cmd.append(";".join(fc_parts))
        
        # Map outputs
        if num_videos > 0:
            cmd.extend(["-map", "[outv]"])
        if num_audios > 0:
            cmd.extend(["-map", "[outa]"])
            
        output_path = os.path.join(temp_dir, output_filename)
        cmd.append(output_path)
        
        logs.append(f"Executing FFmpeg: {' '.join(cmd)}")
        
        # 3. Execute (Mock if no ffmpeg installed, but we try to run it)
        # For the integration test, we will mock this function entirely, so the actual execution here 
        # matters less if ffmpeg is missing in the test env.
        # But for correctness:
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_log = stderr.decode()
            logs.append(f"FFmpeg failed: {error_log}")
            # For robustness, if ffmpeg fails (e.g. not installed), we might want to return a dummy file for testing?
            # No, better to fail and let the test mock handle it.
            return {"error": "FFmpeg compilation failed", "log": logs}
            
        logs.append("FFmpeg success")
        
        return {
            "status": "success",
            "output_path": output_path,
            "temp_dir": temp_dir,
            "duration": 0.0, # Parse if needed
            "log": logs
        }
        
    except Exception as e:
        logs.append(f"Exception: {str(e)}")
        return {"error": str(e), "log": logs}
    finally:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logs.append(f"Cleaned up temp dir: {temp_dir}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup temp dir {temp_dir}: {cleanup_error}")
