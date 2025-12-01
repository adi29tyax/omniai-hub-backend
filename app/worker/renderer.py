import asyncio
import os
import uuid
import logging
import tempfile
from typing import List, Dict, Any
from app.utils.r2_upload import upload_public

logger = logging.getLogger(__name__)

async def run_ffmpeg(args: List[str]):
    """
    Helper to run FFmpeg command asynchronously.
    """
    cmd = ["ffmpeg", "-y"] + args
    logger.info(f"Running FFmpeg: {' '.join(cmd)}")
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        logger.error(f"FFmpeg failed: {stderr.decode()}")
        raise RuntimeError(f"FFmpeg command failed with code {process.returncode}")
    
    return stdout

async def render_animation_block(block: Dict[str, Any], output_path: str):
    """
    Render a single animation block using FFmpeg filters.
    """
    # Placeholder for complex animation logic.
    # In a real implementation, this would generate frames or use complex filter_complex chains.
    # For now, we generate a simple color or test pattern video of the specified duration.
    
    duration = block.get("duration", 2.0)
    # Generate a test source with duration
    # filters: color=c=blue:s=1920x1080:d={duration}
    
    args = [
        "-f", "lavfi",
        "-i", f"color=c=blue:s=1920x1080:d={duration}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    await run_ffmpeg(args)

async def mix_audio_layers(layers: List[Dict[str, Any]], duration: float, output_path: str):
    """
    Mix audio layers into a single audio track.
    """
    if not layers:
        # Generate silent audio
        args = [
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(duration),
            "-c:a", "aac",
            output_path
        ]
        await run_ffmpeg(args)
        return

    # Complex mixing logic would go here.
    # For now, just taking the first layer or generating silence if empty.
    # Real implementation would use -filter_complex amix
    
    # Placeholder: Just generate silence for now to avoid complex input handling without real files
    args = [
        "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=stereo",
        "-t", str(duration),
        "-c:a", "aac",
        output_path
    ]
    await run_ffmpeg(args)

async def encode_final_video(video_parts: List[str], audio_path: str, output_path: str):
    """
    Concatenate video parts and mux with audio.
    """
    # Create concat file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as f:
        concat_file = f.name
        for part in video_parts:
            # Escape paths for ffmpeg concat demuxer
            safe_path = part.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")
    
    try:
        args = [
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        await run_ffmpeg(args)
    finally:
        if os.path.exists(concat_file):
            os.remove(concat_file)

async def generate_video_from_timeline(timeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main worker function to render video from timeline.
    """
    task_id = str(uuid.uuid4())
    logger.info(f"Starting render task {task_id}")
    
    temp_dir = tempfile.mkdtemp()
    video_parts = []
    
    try:
        timeline = timeline_data.get("timeline", [])
        total_duration = 0.0
        
        # 1. Render each block
        for i, block in enumerate(timeline):
            block_duration = block.get("duration", 2.0)
            total_duration += block_duration
            
            part_path = os.path.join(temp_dir, f"part_{i}.mp4")
            await render_animation_block(block, part_path)
            video_parts.append(part_path)
            
        # 2. Mix Audio
        audio_path = os.path.join(temp_dir, "mixed_audio.aac")
        await mix_audio_layers(timeline_data.get("audio_layers", []), total_duration, audio_path)
        
        # 3. Final Encode
        final_output_path = os.path.join(temp_dir, "final_output.mp4")
        await encode_final_video(video_parts, audio_path, final_output_path)
        
        # 4. Upload to R2
        with open(final_output_path, "rb") as f:
            data = f.read()
            upload_result = upload_public(f"render_{task_id}.mp4", data, content_type="video/mp4")
            
        return {
            "task_id": task_id,
            "status": "completed",
            "url": upload_result["url"],
            "key": upload_result["key"]
        }
        
    except Exception as e:
        logger.error(f"Render task {task_id} failed: {e}")
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e)
        }
    finally:
        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
