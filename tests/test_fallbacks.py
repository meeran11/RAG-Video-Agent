import os

from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.summarize import generate_title, summarize


def test_summarize_and_title_fallback_without_mistral(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    transcript = (
        "The team discussed the launch plan for the new product. "
        "We need to finalize the budget by Friday. "
        "Maya will send the updated report next week."
    )

    summary = summarize(transcript)
    title = generate_title(transcript)

    assert summary
    assert title
    assert len(title.split()) <= 8


def test_extraction_fallback_without_mistral(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    transcript = (
        "We need to finalize the budget by Friday. "
        "Maya will send the report. "
        "What about the launch timeline?"
    )

    action_items = extract_action_items(transcript)
    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)

    assert action_items
    assert decisions
    assert questions
