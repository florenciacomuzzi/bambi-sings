#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

docker compose --profile tools run --rm transcribe \
  transcribe \
  --exports-dir /exports \
  --output-dir /output \
  --provider "${TRANSCRIPTION_PROVIDER:-local}" \
  --model "${WHISPER_MODEL:-base}" \
  --device "${WHISPER_DEVICE:-cpu}" \
  --compute-type "${WHISPER_COMPUTE:-int8}" \
  --openai-model "${OPENAI_MODEL:-gpt-4o-mini-transcribe}" \
  "$@"
