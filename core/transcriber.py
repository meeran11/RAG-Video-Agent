import whisper
import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")  # Default to "base" if not set

_model = None

def load_model():
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL)
    return _model

def transcribe_chunk(chunk_path:str,translate:bool=False)->str:
    model = load_model()

    task = "translate" if translate else "transcribe"

    result = model.transcribe(chunk_path, task=task)

    return result["text"]


def transcribe_all(chunks:list , translate:bool = False)->str:
    full_transcript = ""
    for i,chunk in enumerate(chunks):
        transcript = transcribe_chunk(chunk,translate=translate)
        full_transcript += transcript + " "

    return full_transcript