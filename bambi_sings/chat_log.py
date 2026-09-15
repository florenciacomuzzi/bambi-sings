import re
from pathlib import Path

from bambi_sings.attachments import (
    extract_attachment_filename,
    is_audio_omitted,
    resolve_attachment,
)
from bambi_sings.models import Message, Platform

BIDI = "\u200e\u200f\ufeff"

IOS_HEADER = re.compile(
    r"^[" + BIDI + r"]*"
    r"\[(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}(?::\d{2})?"
    r"[\u202f ]?(?:AM|PM))\]\s*([^:]+):\s?(.*)$",
    re.IGNORECASE,
)

ANDROID_HEADER = re.compile(
    r"^[" + BIDI + r"]*"
    r"(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^:]+):\s?(.*)$",
)


def normalize_text(text: str) -> str:
    if text.startswith("\ufeff"):
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")


def find_chat_log(export_root: Path) -> Path:
    chat = export_root / "_chat.txt"
    if chat.is_file():
        return chat
    matches = sorted(export_root.glob("WhatsApp Chat with *.txt"))
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise FileNotFoundError(
            f"Multiple Android chat logs found in {export_root}; expected one."
        )
    raise FileNotFoundError(f"No chat log found under {export_root}")


def _parse_header(line: str) -> tuple[Platform, str, str, str] | None:
    ios = IOS_HEADER.match(line)
    if ios:
        return Platform.IOS, ios.group(1), ios.group(2).strip(), ios.group(3)
    android = ANDROID_HEADER.match(line)
    if android:
        return (
            Platform.ANDROID,
            android.group(1),
            android.group(2).strip(),
            android.group(3),
        )
    return None


def parse_chat_log(text: str, export_root: Path | None = None) -> list[Message]:
    text = normalize_text(text)
    lines = text.split("\n")
    messages: list[Message] = []
    current: Message | None = None
    index = 0

    for line in lines:
        parsed = _parse_header(line)
        if parsed is not None:
            if current is not None:
                messages.append(current)
            platform, ts, sender, body = parsed
            attachment = None
            media_omitted = is_audio_omitted(body)
            filename = extract_attachment_filename(body)
            if filename and export_root is not None:
                attachment = resolve_attachment(filename, export_root)
            current = Message(
                index=index,
                platform=platform,
                timestamp_display=ts,
                sender=sender,
                header_line=line,
                body=body,
                attachment=attachment,
                media_omitted=media_omitted,
            )
            index += 1
        elif current is not None:
            current.continuation_lines.append(line)
        else:
            if line.strip():
                messages.append(
                    Message(
                        index=index,
                        platform=Platform.UNKNOWN,
                        timestamp_display="",
                        sender="",
                        header_line=line,
                        body=line,
                    )
                )
                index += 1

    if current is not None:
        messages.append(current)
    return messages
