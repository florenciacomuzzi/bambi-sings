import pytest

from bambi_sings.transcribe.factory import create_transcriber
from bambi_sings.transcribe.local import LocalWhisperTranscriber
from bambi_sings.transcribe.openai_provider import OpenAITranscriber


def test_create_transcriber_local():
    transcriber = create_transcriber("local", model_size="tiny")
    assert isinstance(transcriber, LocalWhisperTranscriber)
    assert transcriber.model_size == "tiny"


def test_create_transcriber_openai():
    transcriber = create_transcriber("openai", openai_api_key="sk-test")
    assert isinstance(transcriber, OpenAITranscriber)
    assert transcriber.api_key == "sk-test"


def test_create_transcriber_unknown_provider():
    with pytest.raises(ValueError, match="Unknown transcription provider"):
        create_transcriber("carrier-pigeon")
