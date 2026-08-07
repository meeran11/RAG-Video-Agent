import os

from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.summarize import generate_title, summarize
from utils.audio_processor import build_auth_attempts, resolve_cookie_file


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


def test_resolve_cookie_file_falls_back_to_repo_cookie(tmp_path, monkeypatch):
    monkeypatch.delenv("YTDLP_COOKIE_FILE", raising=False)

    cookie_path = tmp_path / "cookies.txt"
    cookie_path.write_text("# test cookie", encoding="utf-8")

    resolved = resolve_cookie_file(base_dir=tmp_path)

    assert resolved == str(cookie_path.resolve())


def test_build_auth_attempts_prefers_cookie_file_then_browser(monkeypatch, tmp_path):
    monkeypatch.delenv("YTDLP_COOKIE_FILE", raising=False)
    monkeypatch.setenv("YTDLP_COOKIES_FROM_BROWSER", "chrome")

    cookie_path = tmp_path / "cookies.txt"
    cookie_path.write_text("# test cookie", encoding="utf-8")

    attempts = build_auth_attempts(base_dir=tmp_path)

    assert attempts[0][0] == "cookiefile"
    assert attempts[0][1]["cookiefile"] == str(cookie_path.resolve())
    assert attempts[1][0] == "cookiesfrombrowser"
