import json
from pathlib import Path

from bambi_sings.transcribe.openai_provider import OpenAITranscriber


def test_transcribe_file_success(tmp_path: Path):
    audio = tmp_path / "x.wav"
    audio.write_bytes(b"wav")
    transcriber = OpenAITranscriber(
        api_key="sk-test",
        request_fn=lambda path: json.dumps({"text": " hello there "}).encode(),
    )
    result = transcriber.transcribe_file(audio)
    assert result.ok
    assert result.text == "hello there"
    assert result.provider == "openai"
    assert result.model == transcriber.model_label


def test_transcribe_file_missing_api_key(tmp_path: Path):
    audio = tmp_path / "x.wav"
    audio.write_bytes(b"wav")
    transcriber = OpenAITranscriber(api_key=None, request_fn=lambda path: b"{}")
    result = transcriber.transcribe_file(audio)
    assert not result.ok
    assert "OPENAI_API_KEY" in result.error


def test_transcribe_file_empty_text(tmp_path: Path):
    audio = tmp_path / "x.wav"
    audio.write_bytes(b"wav")
    transcriber = OpenAITranscriber(
        api_key="sk-test",
        request_fn=lambda path: json.dumps({"text": "  "}).encode(),
    )
    result = transcriber.transcribe_file(audio)
    assert not result.ok
    assert result.error == "empty transcription"


def test_transcribe_file_invalid_json(tmp_path: Path):
    audio = tmp_path / "x.wav"
    audio.write_bytes(b"wav")
    transcriber = OpenAITranscriber(
        api_key="sk-test",
        request_fn=lambda path: b"not json",
    )
    result = transcriber.transcribe_file(audio)
    assert not result.ok
    assert "invalid response" in result.error


def test_transcribe_file_request_error(tmp_path: Path):
    audio = tmp_path / "x.wav"
    audio.write_bytes(b"wav")

    def boom(path):
        raise OSError("connection reset")

    transcriber = OpenAITranscriber(api_key="sk-test", request_fn=boom)
    result = transcriber.transcribe_file(audio)
    assert not result.ok
    assert result.error == "connection reset"


def test_build_multipart_includes_model_and_file(tmp_path: Path):
    audio = tmp_path / "note.wav"
    audio.write_bytes(b"\x00\x01")
    transcriber = OpenAITranscriber(api_key="sk-test", model="gpt-4o-mini-transcribe")
    body = transcriber._build_multipart(audio, "boundary123")
    assert b"name=\"model\"" in body
    assert b"gpt-4o-mini-transcribe" in body
    assert b'filename="note.wav"' in body
    assert b"\x00\x01" in body


def test_api_key_from_environment(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
    transcriber = OpenAITranscriber()
    assert transcriber.api_key == "sk-env"
