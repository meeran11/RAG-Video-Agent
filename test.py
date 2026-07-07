from utils.audio_processor import process_input
from core.transcriber import transcribe_all

src = "https://www.youtube.com/shorts/CY5cUsCPeeU"

chunks = process_input(src)
transcript = transcribe_all(chunks, translate=False)

print("Final Transcript:")
print(transcript)