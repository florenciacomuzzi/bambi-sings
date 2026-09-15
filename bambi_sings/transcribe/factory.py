from typing import Optional

from bambi_sings.transcribe.local import LocalWhisperTranscriber
from bambi_sings.transcribe.openai_provider import DEFAULT_MODEL, OpenAITranscriber
from bambi_sings.transcribe.protocol import Transcriber

PROVIDERS = ("local", "openai")


def create_transcriber(
    provider: str,
    *,
    model_size: str = "base",
    device: str = "cpu",
    compute_type: str = "int8",
    openai_model: str = DEFAULT_MODEL,
    openai_api_key: Optional[str] = None,
) -> Transcriber:
    if provider == "local":
        return LocalWhisperTranscriber(
            model_size=model_size,
            device=device,
            compute_type=compute_type,
        )
    if provider == "openai":
        return OpenAITranscriber(api_key=openai_api_key, model=openai_model)
    raise ValueError(
        f"Unknown transcription provider: {provider!r}; expected one of {PROVIDERS}"
    )
