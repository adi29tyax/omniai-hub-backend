from .utils import call_chatgpt, call_gemini

# ------------------------------
# Hybrid Code Generation (GPT → Gemini)
# ------------------------------
async def generate_code(request):
    generated = await call_chatgpt(
        f"Write {request.language} code for: {request.prompt}"
    )

    reviewed = await call_gemini(
        f"Improve and debug this code:\n{generated}"
    )

    return {
        "generated_code": generated,
        "gemini_review": reviewed
    }


# ------------------------------
# Hybrid Debugging
# ------------------------------
async def debug_code(request):
    improved = await call_gemini(f"Debug this code:\n{request.prompt}")
    return {"debugged_code": improved}


# ------------------------------
# Code Explanation (ChatGPT)
# ------------------------------
async def explain_code(request):
    explanation = await call_chatgpt(f"Explain this code:\n{request.prompt}")
    return {"explanation": explanation}
