FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md setup.cfg ./
COPY bambi_sings ./bambi_sings

RUN pip install --no-cache-dir .

ENV TRANSCRIPTION_PROVIDER=local
ENV WHISPER_MODEL=base
ENV WHISPER_DEVICE=cpu
ENV WHISPER_COMPUTE=int8
ENV OPENAI_MODEL=gpt-4o-mini-transcribe

ENTRYPOINT ["bambi-sings"]
CMD ["transcribe", "--exports-dir", "/exports", "--output-dir", "/output", "--provider", "local", "--model", "base", "--device", "cpu", "--compute-type", "int8", "--openai-model", "gpt-4o-mini-transcribe"]
