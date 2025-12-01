from typing import Dict, Any, List
import logging
import asyncio
from app.modules.director.scene_breakdown import generate_scene_breakdown
from app.modules.director.shot_breakdown import generate_shot_breakdown
from app.modules.director.keyframe_generator import generate_keyframes
from app.modules.director.animation_engine import generate_animation_blocks
from app.modules.director.timeline_compiler import compile_timeline

logger = logging.getLogger(__name__)

OWNER_EMAIL = "csadityasharma2000@gmail.com"

async def auto_direct_episode(payload: Dict[str, Any], user: Any) -> Dict[str, Any]:
    """
    Orchestrates the entire AI Director pipeline:
    Story -> Scenes -> Shots -> Keyframes -> Animation -> Timeline
    """
    
    # 1. Validate Owner Mode
    is_owner = hasattr(user, "email") and user.email == OWNER_EMAIL
    
    story_text = payload.get("story", "")
    if not story_text:
        raise ValueError("Story text is required")

    logger.info(f"Auto-Directing episode for user: {user.email if hasattr(user, 'email') else 'unknown'}")

    # 2. Scene Breakdown
    logger.info("Step 1: Generating Scene Breakdown...")
    scenes = await generate_scene_breakdown(story_text)
    
    # 3. Shot Breakdown (Parallel per scene)
    logger.info("Step 2: Generating Shot Breakdown...")
    async def process_scene(scene):
        shots = await generate_shot_breakdown(scene)
        scene["shots"] = shots
        return scene

    scenes = await asyncio.gather(*(process_scene(scene) for scene in scenes))

    # 4. Keyframe Generation (Parallel per shot)
    logger.info("Step 3: Generating Keyframes...")
    async def process_shot_keyframes(shot):
        keyframes = await generate_keyframes(shot)
        shot["keyframes"] = keyframes
        return shot

    for scene in scenes:
        scene["shots"] = await asyncio.gather(*(process_shot_keyframes(shot) for shot in scene.get("shots", [])))

    # 5. Animation Generation (Parallel per shot)
    logger.info("Step 4: Generating Animation Blocks...")
    async def process_shot_animation(shot):
        # Prepare payload for animation engine
        anim_payload = {
            "keyframes": shot.get("keyframes", []),
            "shot_metadata": shot
        }
        animation_blocks = await generate_animation_blocks(anim_payload, user)
        shot["animation_blocks"] = animation_blocks
        return shot

    for scene in scenes:
        scene["shots"] = await asyncio.gather(*(process_shot_animation(shot) for shot in scene.get("shots", [])))

    # 6. Audio Generation (Stub/Placeholder for now as it requires DB access usually)
    # In a full flow, we would call audio_service functions here.
    # For now, we'll assume audio layers are generated or empty.
    audio_layers = [] 

    # 7. Timeline Compilation
    logger.info("Step 5: Compiling Timeline...")
    compile_payload = {
        "scenes": scenes,
        "audio_layers": audio_layers,
        "resolution": payload.get("resolution", "1920x1080"),
        "fps": payload.get("fps", 24)
    }
    
    compiled_result = await compile_timeline(compile_payload, user)

    return {
        "episode": {
            "title": payload.get("title", "Untitled Episode"),
            "story": story_text
        },
        "timeline": compiled_result.get("timeline", []),
        "ffmpeg_blueprint": compiled_result.get("ffmpeg_blueprint", {}),
        "scenes": scenes,
        "status": "episode_generated"
    }
