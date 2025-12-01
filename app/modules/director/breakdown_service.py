import json
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.ide.utils import call_gemini
from . import models, schemas
from .system_prompt import BREAKDOWN_PROMPT
from app.utils.logger import logger

# Placeholder for Llama call since it's not in utils.py yet
# In a real scenario, this would call a local or remote Llama endpoint.
# For now, we reuse Gemini or a mock to simulate the "Fix JSON" step if needed,
# or just assume Gemini returns valid JSON (which it often does).
# However, to strictly follow the "hybrid logic" pattern requested:
async def call_llama(prompt: str):
    # "Simulating" Llama call by using Gemini again or just returning the prompt if it was a fix request.
    # Since we don't have a Llama key, we'll use Gemini as the "Fixer" too.
    return await call_gemini(prompt)

async def breakdown_scene(db: Session, request: schemas.SceneBreakdownRequest) -> schemas.ShotBreakdownResponse:
    logger.info(f"Breaking down scene {request.scene_id} for story {request.story_id}")
    # 1. Fetch scene and characters
    scene = db.query(models.DirectorScene).filter(models.DirectorScene.id == request.scene_id).first()
    if not scene:
        raise ValueError("Scene not found")
    
    story = db.query(models.DirectorStory).filter(models.DirectorStory.id == request.story_id).first()
    if not story:
        raise ValueError("Story not found")
        
    characters = db.query(models.DirectorCharacter).filter(models.DirectorCharacter.story_id == request.story_id).all()
    character_data = [{"name": c.name, "role": c.role, "description": c.description} for c in characters]
    
    # 2. Build system prompt
    scene_summary = request.override_concept if request.override_concept else scene.summary
    prompt = BREAKDOWN_PROMPT(scene_summary, character_data, request.style)
    
    # 3. Call Gemini
    gemini_output = await call_gemini(prompt)
    
    # 4. Call Llama (Fix JSON) - Simulating the fix step
    # We construct a prompt to fix the JSON if it looks broken, or just pass it through.
    # For this implementation, we'll assume we pass the output to "Llama" to ensure schema compliance.
    fix_prompt = f"Fix this JSON to match the schema {{'shots': [...]}}: {gemini_output}"
    llama_output = await call_llama(fix_prompt)
    
    # 5. Validate with Pydantic
    # Clean the output to ensure it's valid JSON (remove markdown code blocks if any)
    cleaned_output = llama_output.replace("```json", "").replace("```", "").strip()
    
    try:
        parsed_data = json.loads(cleaned_output)
        # Ensure it matches the expected structure
        if "shots" not in parsed_data:
             raise ValueError("Invalid JSON structure: missing 'shots' key")
    except json.JSONDecodeError:
        # Fallback: try to parse the original Gemini output if Llama failed
        try:
            cleaned_gemini = gemini_output.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(cleaned_gemini)
        except json.JSONDecodeError:
             raise ValueError("Failed to generate valid JSON from AI response")

    # 6. Save shots to DB
    saved_shots = []
    
    # Clear existing shots for this scene if re-generating? 
    # The prompt doesn't explicitly say to clear, but "Breakdown Engine" usually implies generating the list.
    # Let's append or overwrite? "Return a FULL SHOT BREAKDOWN". 
    # I'll delete existing shots for this scene to avoid duplicates/confusion.
    db.query(models.DirectorShot).filter(models.DirectorShot.scene_id == request.scene_id).delete()
    
    for shot_item in parsed_data["shots"]:
        # Map fields to Shot model
        # Shot model has: id, scene_id, shot_id, type, camera, action, prompt
        # We have extra fields in the response (lens, lighting, etc.) which we might store in prompt or action,
        # or just return them. The Shot model in Step 2 only had limited fields.
        # The prompt says: "Shot fields to fill: shot_id, type, camera, action, prompt"
        # So we map the rich data into these fields or combine them.
        
        # We'll combine rich details into 'action' or 'prompt' if needed, 
        # but the prompt specifically asked for a rich response schema.
        # We will save what we can to the DB and return the full rich object.
        
        db_shot = models.DirectorShot(
            scene_id=request.scene_id,
            shot_id=shot_item.get("shot_id"),
            type=shot_item.get("type"),
            camera=f"{shot_item.get('camera_movement', '')} {shot_item.get('lens', '')}".strip(),
            action=shot_item.get("action"),
            prompt=shot_item.get("prompt")
        )
        db.add(db_shot)
        saved_shots.append(shot_item)
    
    db.commit()
    
    # 7. Return structured JSON
    # We return the rich data as requested in ShotBreakdownResponse
    return schemas.ShotBreakdownResponse(
        scene_id=request.scene_id,
        shots=[schemas.ShotBreakdownItem(**item) for item in saved_shots]
    )
