import whisper
import os

WHISPER_MODEL = (os.getenv("WHISPER_MODEL") or "small").strip().lower()

_model = None


def load_model():
    global _model
    if _model is None:
        cache_root = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
        try:
            _model = whisper.load_model(WHISPER_MODEL, download_root=cache_root)
        except OSError:
            cache_file = os.path.join(cache_root, f"{WHISPER_MODEL}.pt")
            if os.path.exists(cache_file):
                os.remove(cache_file)
            _model = whisper.load_model(WHISPER_MODEL, download_root=cache_root)
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