import os

WHISPER_MODEL = ("base").strip().lower()

_model = None


def load_model():
    global _model

    if _model is None:
        from faster_whisper import WhisperModel

        _model = WhisperModel(
            WHISPER_MODEL,
            device="cpu",
            compute_type="int8",
        )

    return _model


def transcribe_chunk(chunk_path: str, translate: bool = False) -> str:
    model = load_model()

    task = "translate" if translate else "transcribe"

    segments, info = model.transcribe(
        chunk_path,
        beam_size=3,
        task=task,
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