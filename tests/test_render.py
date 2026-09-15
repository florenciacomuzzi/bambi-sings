from bambi_sings.models import Message, Platform, TranscriptionResult
from bambi_sings.render import format_transcription_line, render_chat_log


def test_format_transcription_line():
    message = Message(
        index=0,
        platform=Platform.IOS,
        timestamp_display="1/2/24, 10:01:00 AM",
        sender="Bob",
        header_line="",
        body="",
    )
    result = TranscriptionResult(
        text="Hello world",
        provider="local",
        model="faster-whisper/base",
    )
    line = format_transcription_line(message, result)
    assert "[transcription via local/faster-whisper/base]" in line
    assert line.endswith("Hello world")


def test_format_transcription_failed():
    message = Message(
        index=0,
        platform=Platform.IOS,
        timestamp_display="1/2/24, 10:01:00 AM",
        sender="Bob",
        header_line="",
    )
    result = TranscriptionResult(
        text="",
        provider="local",
        model="faster-whisper/base",
        error="boom",
    )
    assert "[transcription failed: boom]" in format_transcription_line(message, result)


def test_render_inserts_after_message():
    message = Message(
        index=1,
        platform=Platform.IOS,
        timestamp_display="1/2/24, 10:01:00 AM",
        sender="Bob",
        header_line="[1/2/24, 10:01:00 AM] Bob: attached",
    )
    result = TranscriptionResult(
        text="spoken",
        provider="local",
        model="faster-whisper/base",
    )
    rendered = render_chat_log([message], {1: result})
    assert rendered.count("\n") >= 2
    assert "spoken" in rendered
