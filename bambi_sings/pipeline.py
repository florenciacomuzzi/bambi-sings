import logging
import tempfile
from pathlib import Path

from bambi_sings.archive import build_zip, extract_zip
from bambi_sings.attachments import is_voice_note
from bambi_sings.audio import convert_to_wav
from bambi_sings.chat_log import find_chat_log, parse_chat_log
from bambi_sings.discovery import discover_export_zip, transcribed_zip_name
from bambi_sings.models import TranscriptionResult
from bambi_sings.render import render_chat_log
from bambi_sings.transcribe.factory import create_transcriber
from bambi_sings.transcribe.openai_provider import DEFAULT_MODEL as OPENAI_DEFAULT_MODEL
from bambi_sings.transcribe.protocol import Transcriber

logger = logging.getLogger(__name__)


class TranscriptionPipeline:
    def __init__(
        self,
        exports_dir: Path,
        output_dir: Path,
        zip_path: Path | None = None,
        dry_run: bool = False,
        limit: int | None = None,
        provider: str = "local",
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        openai_model: str = OPENAI_DEFAULT_MODEL,
        ffmpeg_executable: str = "ffmpeg",
        transcriber: Transcriber | None = None,
    ) -> None:
        self.exports_dir = exports_dir
        self.output_dir = output_dir
        self.zip_path = zip_path
        self.dry_run = dry_run
        self.limit = limit
        self.ffmpeg_executable = ffmpeg_executable
        self.transcriber = transcriber or create_transcriber(
            provider,
            model_size=model_size,
            device=device,
            compute_type=compute_type,
            openai_model=openai_model,
        )

    def run(self) -> Path | None:
        source_zip = discover_export_zip(self.exports_dir, self.zip_path)
        logger.info("Using export %s", source_zip.name)

        with tempfile.TemporaryDirectory(prefix="bambi-sings-") as temp:
            root = Path(temp)
            work_dir = root / "export"
            cache_dir = root / "cache"
            work_dir.mkdir()
            cache_dir.mkdir()
            extract_zip(source_zip, work_dir)
            chat_path = find_chat_log(work_dir)
            original_text = chat_path.read_text(encoding="utf-8")
            messages = parse_chat_log(original_text, export_root=work_dir)

            voice_messages = [
                message
                for message in messages
                if is_voice_note(message.attachment, message.body)
            ]
            if self.limit is not None:
                voice_messages = voice_messages[: self.limit]

            logger.info(
                "Found %d voice note(s) to transcribe",
                len(voice_messages),
            )
            if self.dry_run:
                for message in voice_messages:
                    assert message.attachment is not None
                    logger.info(
                        "  [%s] %s -> %s",
                        message.timestamp_display,
                        message.sender,
                        message.attachment.filename,
                    )
                return None

            transcriptions: dict[int, TranscriptionResult] = {}
            wav_dir = cache_dir

            for message in voice_messages:
                attachment = message.attachment
                assert attachment is not None and attachment.resolved_path is not None
                wav_path = wav_dir / f"{attachment.filename}.wav"
                logger.info("Transcribing %s", attachment.filename)
                convert_to_wav(
                    attachment.resolved_path,
                    wav_path,
                    ffmpeg_executable=self.ffmpeg_executable,
                )
                result = self.transcriber.transcribe_file(wav_path)
                if not result.ok:
                    logger.warning(
                        "Transcription issue for %s: %s",
                        attachment.filename,
                        result.error or "empty text",
                    )
                transcriptions[message.index] = result

            updated = render_chat_log(messages, transcriptions)
            chat_path.write_text(updated, encoding="utf-8")

            output_zip = self.output_dir / transcribed_zip_name(source_zip)
            build_zip(work_dir, output_zip)
            logger.info("Wrote %s", output_zip)
            return output_zip
