def STORY_ENGINE_PROMPT(concept, style):
    return f"""
    You are a world-class Anime Director and Screenwriter.
    Your task is to generate a full, structured story for a 10-12 minute anime episode based on the following concept:
    
    CONCEPT: "{concept}"
    STYLE: "{style}"

    You must output strictly valid JSON following this structure:
    {{
      "title": "Episode Title",
      "logline": "One sentence summary",
      "theme": "Core theme",
      "setting": "World description",
      "style": "{style}",
      "characters": [
        {{
          "name": "Name",
          "role": "Protagonist/Antagonist/Support",
          "description": "Physical appearance",
          "personality": "Traits",
          "visual_style": "Clothing/Colors",
          "voice_style": "Tone/Pitch"
        }}
      ],
      "scenes": [
        {{
          "scene_id": "SCENE-01",
          "title": "Scene Title",
          "summary": "What happens",
          "location": "Specific place",
          "time_of_day": "Day/Night",
          "shots": [
            {{
              "shot_id": "SHOT-01",
              "type": "Wide/Close-up/Medium",
              "camera": "Static/Pan/Zoom",
              "action": "Visual description of action",
              "prompt": "Detailed image generation prompt for this shot"
            }}
          ]
        }}
      ]
    }}

    REQUIREMENTS:
    - Create at least 3 main characters.
    - Create at least 5 scenes.
    - Each scene must have at least 3 shots.
    - Use cinematic camera language.
    - Ensure the JSON is valid and parseable.
    """

def BREAKDOWN_PROMPT(scene_summary, characters, style):
    return f"""
    You are a world-class Anime Director and Cinematographer.
    Your task is to break down the following scene into a detailed, cinematic shot list.
    
    SCENE SUMMARY: "{scene_summary}"
    CHARACTERS: {characters}
    STYLE: "{style}"

    INSTRUCTIONS:
    - Break the scene into 8–15 cinematic shots.
    - Include shot type (wide, mid, close-up, extreme close-up).
    - Include lens choice (e.g., 24mm, 35mm, 50mm, 85mm).
    - Include camera movement (pan, tilt, dolly, crane, handheld).
    - Include environment details, lighting, and mood.
    - Include specific character poses and actions.
    - Incorporate the requested anime visual style.
    - Define color palette and emotion for each shot.
    - Include transition notes between shots.
    - Return STRICT JSON following the schema below.

    JSON SCHEMA:
    {{
      "shots": [
        {{
          "shot_id": "SHOT-01",
          "type": "Wide/Mid/Close-up",
          "lens": "35mm",
          "camera_movement": "Dolly In",
          "environment": "Description of background/setting",
          "lighting": "Lighting setup (e.g., Rembrandt, Soft, Backlit)",
          "action": "What happens in the shot",
          "emotion": "Emotional tone",
          "color_palette": "Dominant colors",
          "transition": "Cut/Dissolve/Fade",
          "prompt": "Highly detailed image generation prompt for this shot"
        }}
      ]
    }}
    """

def KEYFRAME_PROMPT(shot, style, characters):
    return f"""
    You are a world-class Anime Concept Artist and Cinematographer.
    Your task is to create a highly detailed, camera-aware, cinematic anime keyframe prompt for the following shot.
    
    SHOT DETAILS:
    Type: {shot.type}
    Camera: {shot.camera}
    Action: {shot.action}
    Original Prompt: {shot.prompt}
    
    STYLE: "{style}"
    CHARACTERS: {characters}

    INSTRUCTIONS:
    - Create a prompt optimized for Flux.1-dev / Niji style generation.
    - Focus on visual details: lighting, composition, lens effects, color grading.
    - Describe the character's pose, expression, and outfit in detail based on the character data.
    - Describe the environment and background.
    - DO NOT generate a full scene script, only a single keyframe description.
    - Output STRICT JSON following the structure below.

    JSON SCHEMA:
    {{
      "positive": "Full detailed positive prompt...",
      "negative": "Negative prompt (e.g., low quality, bad anatomy...)",
      "camera": "Camera settings (e.g., 35mm, f/1.8, bokeh)",
      "lens": "Lens details",
      "lighting": "Lighting description",
      "style": "Style keywords",
      "details": "Additional visual details"
    }}
    """

def ANIMATION_PROMPT(shot, keyframe_prompt, style):
    return f"""
    You are a world-class Anime Animation Director.
    Your task is to create a video-generation-ready prompt for the following shot, based on the keyframe and shot details.
    
    SHOT DETAILS:
    Camera Movement: {shot.camera}
    Action: {shot.action}
    
    KEYFRAME PROMPT: "{keyframe_prompt}"
    STYLE: "{style}"

    INSTRUCTIONS:
    - Translate the static keyframe description into a dynamic motion description.
    - Focus on cinematic motion: {shot.camera}.
    - Describe lens and framing.
    - Preserve character identity, outfit, and style from the keyframe.
    - Expand on environment and lighting details.
    - Add specific motion beats (e.g., hair blowing, clothing movement, physics, particle effects).
    - Add anime conventions (e.g., speed lines, bloom, rim lights, impact frames).
    - Create a refined prompt suitable for high-end video models (Luma, Pika, Runway, Kling).
    - Output STRICT JSON following the structure below.

    JSON SCHEMA:
    {{
      "positive": "Full detailed video generation prompt...",
      "negative": "Negative prompt...",
      "motion": "Description of motion and camera movement",
      "camera": "Camera settings",
      "lighting": "Lighting details",
      "style": "Style keywords",
      "details": "Additional animation details"
    }}
    """

def AUDIO_PROMPT(character, text, emotion):
    return f"""
    You are an expert Voice Director.
    Your task is to generate a detailed emotional profile and TTS prompt for the following line of dialogue.
    
    CHARACTER: {character}
    TEXT: "{text}"
    EMOTION: "{emotion}"

    INSTRUCTIONS:
    - Analyze the text and emotion.
    - Determine the appropriate pitch, speed, and intensity.
    - Describe the speaking style (e.g., whisper, shout, shaky, confident).
    - Output STRICT JSON.

    JSON SCHEMA:
    {{
      "emotion_profile": {{
        "primary_emotion": "...",
        "intensity": 0.8,
        "pitch": "high/medium/low",
        "speed": "fast/medium/slow"
      }},
      "tts_prompt": "Description of how the line should be read..."
    }}
    """

def MUSIC_PROMPT(scene_mood, pacing):
    return f"""
    You are a world-class Anime Music Composer.
    Your task is to compose a background music track for a scene.
    
    MOOD: "{scene_mood}"
    PACING: "{pacing}"

    INSTRUCTIONS:
    - Describe the instrumentation, tempo, and musical style.
    - Output STRICT JSON.

    JSON SCHEMA:
    {{
      "genre": "...",
      "tempo": 120,
      "instruments": ["piano", "violin", ...],
      "description": "Full musical description..."
    }}
    """

def SFX_PROMPT(action):
    return f"""
    You are an expert Sound Designer.
    Your task is to list the sound effects needed for the following action.
    
    ACTION: "{action}"

    INSTRUCTIONS:
    - Identify all necessary sound effects (footsteps, impacts, ambience, etc.).
    - Output STRICT JSON.

    JSON SCHEMA:
    {{
      "sfx_list": [
        {{
          "name": "footsteps_concrete",
          "type": "foley",
          "description": "Heavy boots walking on concrete"
        }},
        ...
      ]
    }}
    """
