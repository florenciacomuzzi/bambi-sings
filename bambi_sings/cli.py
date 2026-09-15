import argparse
import logging
import sys
from pathlib import Path

from bambi_sings.pipeline import TranscriptionPipeline
from bambi_sings.transcribe.openai_provider import DEFAULT_MODEL as OPENAI_DEFAULT_MODEL


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bambi-sings",
        description="Transcribe WhatsApp voice notes in exported chat zips.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    transcribe = subparsers.add_parser(
        "transcribe",
        help="Unzip export, transcribe voice notes, write output zip.",
    )
    transcribe.add_argument(
        "--exports-dir",
        type=Path,
        default=Path("exports"),
        help="Directory containing a single WhatsApp .zip export.",
    )
    transcribe.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for the _transcribed.zip result.",
    )
    transcribe.add_argument(
        "--zip",
        type=Path,
        default=None,
        help="Explicit export zip path (overrides discovery).",
    )
    transcribe.add_argument(
        "--dry-run",
        action="store_true",
        help="List voice notes without transcribing.",
    )
    transcribe.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Transcribe at most N voice notes (development).",
    )
    transcribe.add_argument(
        "--provider",
        choices=["local", "openai"],
        default="local",
        help="Transcription backend: free on-device faster-whisper (local, "
        "default) or OpenAI's hosted API (openai; needs OPENAI_API_KEY).",
    )
    transcribe.add_argument(
        "--model",
        default="base",
        help="faster-whisper model size (tiny, base, small, medium, large-v3).",
    )
    transcribe.add_argument(
        "--device",
        default="cpu",
        help="Inference device for faster-whisper (cpu or cuda).",
    )
    transcribe.add_argument(
        "--compute-type",
        default="int8",
        help="CTranslate2 compute type (e.g. int8, float16).",
    )
    transcribe.add_argument(
        "--openai-model",
        default=OPENAI_DEFAULT_MODEL,
        help="OpenAI transcription model (used when --provider openai).",
    )
    transcribe.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    if args.command == "transcribe":
        pipeline = TranscriptionPipeline(
            exports_dir=args.exports_dir,
            output_dir=args.output_dir,
            zip_path=args.zip,
            dry_run=args.dry_run,
            limit=args.limit,
            provider=args.provider,
            model_size=args.model,
            device=args.device,
            compute_type=args.compute_type,
            openai_model=args.openai_model,
        )
        result = pipeline.run()
        if result is None and args.dry_run:
            sys.exit(0)
        if result is None:
            sys.exit(1)
        sys.exit(0)

    parser.error(f"Unknown command: {args.command}")
