from bambi_sings.models import Message, Platform, TranscriptionResult


def test_transcription_result_ok():
    assert TranscriptionResult("hi", "local", "m").ok
    assert not TranscriptionResult("", "local", "m", error="x").ok


def test_message_format_header_prefix():
    ios = Message(
        index=0,
        platform=Platform.IOS,
        timestamp_display="t",
        sender="A",
        header_line="",
    )
    assert ios.format_header_prefix() == "[t] A: "
    android = Message(
        index=1,
        platform=Platform.ANDROID,
        timestamp_display="d",
        sender="B",
        header_line="",
    )
    assert android.format_header_prefix().startswith("d - B:")
