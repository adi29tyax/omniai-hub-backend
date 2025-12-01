from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.director_schemas.director import (

    StoryEngineRequest,
    StoryEngineResponse,
)
from app.models.director import Scene, Shot, Character
from app.models import Project

router = APIRouter(prefix="/director", tags=["Director"])


# ---------------------------
# MOCK STORY ENGINE (TEMP)
# ---------------------------

def mock_story_engine(req: StoryEngineRequest):
    """
    This function simulates Gemini/Llama responses.
    Later we will replace this with real Gemini API call.
    """

    return {
        "title": "The Neon Samurai",
        "logline": "A lone samurai confronts a robot in neon-soaked streets.",
        "characters": [
            {
                "name": "Hiro",
                "visual_traits": "white hair, red cybernetic eye, black tactical coat"
            },
            {
                "name": "Unit-7",
                "visual_traits": "tall armored robot, glowing blue core"
            }
        ],
        "scenes": [
            {
                "scene_number": 1,
                "location": "EXT. CYBERPUNK ALLEY - NIGHT",
                "shots": [
                    {
                        "shot_number": 1,
                        "camera_angle": "Wide Shot",
                        "subject": "Alleyway",
                        "action": "Rain falls. Neon signs flicker.",
                        "visual_prompt": "(anime style) neon street, rain reflections, cyberpunk atmosphere",
                        "dialogue": None,
                        "audio_mood": "Rain + distant city hum"
                    },
                    {
                        "shot_number": 2,
                        "camera_angle": "Close-up",
                        "subject": "Hiro",
                        "action": "Eyes glowing red slightly.",
                        "visual_prompt": "(anime style) close up of samurai with white hair and red eye, neon rain",
                        "dialogue": "Unit-7… show yourself.",
                        "audio_mood": "Tense music"
                    }
                ]
            }
        ]
    }


# -----------------------------------------------------
#               MAIN ENDPOINT
# -----------------------------------------------------

@router.post("/generate-script", response_model=StoryEngineResponse)
def generate_script(payload: StoryEngineRequest, db: Session = Depends(get_db)):
    """
    Story Engine endpoint:
    1. Calls LLM (currently mock)
    2. Saves Characters, Scenes, Shots to DB
    3. Returns structured story JSON
    """

    # Check project exists
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Step 1 - call LLM (mock for now)
    story = mock_story_engine(payload)

    # Step 2 - Save Characters
    for ch in story["characters"]:
        db_char = Character(
            id=str(uuid.uuid4()),
            project_id=payload.project_id,
            name=ch["name"],
            visual_traits=ch["visual_traits"]
        )
        db.add(db_char)

    db.commit()

    # Step 3 - Save Scenes & Shots
    scene_outputs = []

    for sc in story["scenes"]:
        scene_id = str(uuid.uuid4())

        db_scene = Scene(
            id=scene_id,
            project_id=payload.project_id,
            scene_number=sc["scene_number"],
            location=sc["location"]
        )
        db.add(db_scene)
        db.commit()

        shot_outputs = []

        for sh in sc["shots"]:
            shot_id = str(uuid.uuid4())

            db_shot = Shot(
                id=shot_id,
                scene_id=scene_id,
                shot_number=sh["shot_number"],
                camera_angle=sh["camera_angle"],
                subject=sh["subject"],
                action=sh["action"],
                visual_prompt=sh["visual_prompt"],
                dialogue=sh["dialogue"],
                audio_mood=sh["audio_mood"]
            )

            db.add(db_shot)
            shot_outputs.append(db_shot)

        db.commit()

        scene_outputs.append(db_scene)

    # Step 4 - return story to frontend
    return story
