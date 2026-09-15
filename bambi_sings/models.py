from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class MediaKind(str, Enum):
    PHOTO = "photo"
    AUDIO = "audio"
    VIDEO = "video"
    STICKER = "sticker"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class Platform(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    UNKNOWN = "unknown"


@dataclass
class Attachment:
    filename: str
    media_kind: MediaKind
    resolved_path: Optional[Path] = None


@dataclass
class Message:
    index: int
    platform: Platform
    timestamp_display: str
    sender: str
    header_line: str
    continuation_lines: list[str] = field(default_factory=list)
    body: str = ""
    attachment: Optional[Attachment] = None
    media_omitted: bool = False

    @property
    def line_count(self) -> int:
        return 1 + len(self.continuation_lines)

    def format_header_prefix(self) -> str:
        if self.platform == Platform.IOS:
            return f"[{self.timestamp_display}] {self.sender}: "
        if self.platform == Platform.ANDROID:
            return f"{self.timestamp_display} - {self.sender}: "
        return f"[{self.timestamp_display}] {self.sender}: "


@dataclass
class TranscriptionResult:
    text: str
    provider: str
    model: str
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.text.strip())
