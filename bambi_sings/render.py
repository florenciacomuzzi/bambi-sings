from bambi_sings.models import Message, TranscriptionResult


def format_transcription_line(message: Message, result: TranscriptionResult) -> str:
    prefix = message.format_header_prefix()
    if result.error and not result.text.strip():
        body = f"[transcription failed: {result.error}]"
    elif result.error:
        body = (
            f"[transcription via {result.provider}/{result.model}] "
            f"{result.text.strip()} (partial: {result.error})"
        )
    else:
        body = (
            f"[transcription via {result.provider}/{result.model}] "
            f"{result.text.strip()}"
        )
    return f"{prefix}{body}"


def render_chat_log(
    messages: list[Message],
    transcriptions: dict[int, TranscriptionResult],
) -> str:
    output_lines: list[str] = []
    for message in messages:
        output_lines.append(message.header_line)
        output_lines.extend(message.continuation_lines)
        result = transcriptions.get(message.index)
        if result is not None:
            output_lines.append(format_transcription_line(message, result))
    text = "\n".join(output_lines)
    if output_lines:
        text += "\n"
    return text
