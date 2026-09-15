from unittest.mock import patch

import pytest

from bambi_sings.cli import main


def test_cli_transcribe_dry_run(capsys):
    with patch("bambi_sings.cli.TranscriptionPipeline") as mock_pipeline:
        instance = mock_pipeline.return_value
        instance.run.return_value = None
        with pytest.raises(SystemExit) as excinfo:
            main(["transcribe", "--dry-run"])
    assert excinfo.value.code == 0
    mock_pipeline.assert_called_once()
    _, kwargs = mock_pipeline.call_args
    assert kwargs["provider"] == "local"


def test_cli_transcribe_selects_openai_provider():
    with patch("bambi_sings.cli.TranscriptionPipeline") as mock_pipeline:
        instance = mock_pipeline.return_value
        instance.run.return_value = None
        with pytest.raises(SystemExit) as excinfo:
            main(["transcribe", "--dry-run", "--provider", "openai"])
    assert excinfo.value.code == 0
    _, kwargs = mock_pipeline.call_args
    assert kwargs["provider"] == "openai"
    assert kwargs["openai_model"]


def test_cli_transcribe_failure_exits_nonzero():
    with patch("bambi_sings.cli.TranscriptionPipeline") as mock_pipeline:
        instance = mock_pipeline.return_value
        instance.run.return_value = None
        with pytest.raises(SystemExit) as excinfo:
            main(["transcribe"])
    assert excinfo.value.code == 1
