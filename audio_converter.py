from elevenlabs import generate, set_api_key
import os

set_api_key(os.getenv("ELEVENLABS_API_KEY"))

def generate_audio(text):
    audio = generate(
        text=text,
        voice="Antoni",
        model="eleven_monolingual_v1"
    )
    return audio