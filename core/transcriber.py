from faster_whisper import WhisperModel
import os

WHISPER_MODEL = (os.getenv("WHISPER_MODEL") or "small").strip().lower()

_model = None


def load_model():
    global _model

    if _model is None:
        _model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8"
        )

    return _model


def transcribe_chunk(chunk_path: str, translate: bool = False) -> str:
    model = load_model()

    task = "translate" if translate else "transcribe"

    segments, info = model.transcribe(
        chunk_path,
        beam_size=5,
        task=task
    )

    text = " ".join(segment.text for segment in segments)
    return text.strip()


def transcribe_all(chunks: list, translate: bool = False) -> str:
    transcripts = []

    for chunk in chunks:
        transcripts.append(
            transcribe_chunk(chunk, translate=translate)
        )

    return " ".join(transcripts)