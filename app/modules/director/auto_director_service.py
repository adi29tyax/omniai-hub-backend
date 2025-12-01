import json
import asyncio
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any

from app.modules.ide.utils import call_gemini
from . import (
    models, 
    schemas, 
    service as director_service,
    breakdown_service,
    keyframe_service,
    animation_service,
    audio_service,
    timeline_service
)
from .auto_director_prompt import STORY_GENERATION_PROMPT
from app.utils.logger import logger

async def generate_story(db: Session, project_id: UUID, concept: str, style: str, duration: int) -> models.DirectorStory:
    logger.info(f"Auto-Director: Generating story for concept '{concept}'")
    # 1. Call Gemini to generate story structure
    prompt = STORY_GENERATION_PROMPT(concept, style, duration)
    gemini_output = await call_gemini(prompt)
    
    # 2. Parse JSON
    cleaned_output = gemini_output.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned_output)
    except json.JSONDecodeError:
        # Simple retry or fail
        raise ValueError("Failed to parse story JSON from AI")

    # 3. Create Story in DB
    story_in = schemas.DirectorStoryCreate(
        project_id=project_id,
        title=data.get("title", "Untitled Story"),
        logline=data.get("logline", ""),
        theme=data.get("theme", ""),
        genre=style
    )
    db_story = director_service.create_story(db, story_in)
    
    # 4. Create Characters
    for char_data in data.get("characters", []):
        char_in = schemas.CharacterCreate(
            story_id=db_story.id,
            name=char_data["name"],
            role=char_data.get("role", "Support"),
            description=char_data.get("description", ""),
            personality=char_data.get("personality", ""),
            visual_style=char_data.get("visual_style", style),
            voice_style=char_data.get("voice_type", "")
        )
        director_service.create_character(db, char_in)
        
    # 5. Create Scenes
    for i, scene_data in enumerate(data.get("scenes", [])):
        scene_in = schemas.SceneCreate(
            story_id=db_story.id,
            scene_id=str(i+1),
            title=scene_data["title"],
            summary=scene_data["summary"],
            location=scene_data.get("location", "Unknown"),
            time_of_day=scene_data.get("time_of_day", "Day")
        )
        director_service.create_scene(db, scene_in)
        
    return db_story

async def generate_full_episode(
    db: Session, 
    project_id: UUID, 
    concept: str, 
    style: str, 
    duration: int
) -> Dict[str, Any]:
    logger.info(f"Auto-Director: Starting full episode generation for project {project_id}")
    logs = []
    
    try:
        # 1. STORY ENGINE
        logs.append("Starting Story Engine...")
        story = await generate_story(db, project_id, concept, style, duration)
        logs.append(f"Story generated: {story.title}")
        
        scenes = director_service.get_scenes_by_story(db, story.id)
        logs.append(f"Generated {len(scenes)} scenes.")
        
        scene_order = []
        
        for scene in scenes:
            logs.append(f"Processing Scene: {scene.title}")
            scene_order.append(scene.id)
            
            # 2. BREAKDOWN ENGINE
            logs.append(f"  - Breaking down scene...")
            breakdown_req = schemas.SceneBreakdownRequest(
                scene_id=scene.id,
                story_id=story.id,
                style=style
            )
            # This service saves shots to DB
            await breakdown_service.breakdown_scene(db, breakdown_req)
            
            shots = director_service.get_shots_by_scene(db, scene.id)
            logs.append(f"  - Generated {len(shots)} shots.")
            
            for shot in shots:
                logs.append(f"    > Processing Shot {shot.shot_id}...")
                
                # 3. KEYFRAME ENGINE
                logs.append(f"      - Generating Keyframe...")
                kf_req = schemas.KeyframeRequest(
                    project_id=project_id,
                    scene_id=scene.id,
                    shot_id=shot.id,
                    style=style
                )
                await keyframe_service.generate_keyframe(db, kf_req)
                
                # 4. ANIMATION ENGINE
                logs.append(f"      - Generating Animation...")
                anim_req = schemas.AnimationRequest(
                    project_id=project_id,
                    scene_id=scene.id,
                    shot_id=shot.id,
                    model="Luma-Dream-Machine", # Default
                    duration=4 # Default 4s
                )
                await animation_service.generate_animation(db, anim_req)
                
                # 5. AUDIO ENGINE
                # Voice
                if shot.action and "dialogue" in shot.action.lower(): # Simple heuristic
                    # In a real system, we'd parse dialogue from the shot breakdown or story
                    # For now, we'll skip voice if no explicit text, or generate generic ambience
                    pass
                
                # SFX
                logs.append(f"      - Generating SFX...")
                sfx_req = schemas.SfxRequest(
                    project_id=project_id,
                    scene_id=scene.id,
                    shot_id=shot.id,
                    action_description=shot.action or "ambient noise"
                )
                await audio_service.generate_sfx(db, sfx_req)
            
            # Scene BGM
            logs.append(f"  - Generating Scene BGM...")
            bgm_req = schemas.BgmRequest(
                project_id=project_id,
                scene_id=scene.id,
                mood=style, # Simplified
                pacing="Medium"
            )
            await audio_service.generate_bgm(db, bgm_req)
            
        # 6. TIMELINE & RENDER ENGINE
        logs.append("Compiling Timeline and Rendering Episode...")
        timeline_req = schemas.TimelineRequest(
            project_id=project_id,
            episode_title=story.title,
            scene_order=scene_order,
            export_format="mp4"
        )
        
        timeline_res = await timeline_service.compile_episode(db, timeline_req)
        logs.append("Episode Rendered Successfully!")
        logs.append(f"Final URL: {timeline_res.url}")
        
        return {
            "episode_url": timeline_res.url,
            "story_id": str(story.id),
            "logs": logs
        }
        
    except Exception as e:
        logs.append(f"CRITICAL ERROR: {str(e)}")
        # Re-raise or return error state
        raise e
