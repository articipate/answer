<img width="30" height="30" alt="Answer_Logo" src="https://github.com/user-attachments/assets/a575e8cd-5d8c-45bd-bcff-5249a10f2b83" />


# Answer

Open-source desktop application to generate datasets from documents using AI APIs. Create high-quality training data by transforming PDFs, Word documents, text files, and Markdown into structured datasets.

## Features

- **Multi-provider support**: OpenAI, Anthropic, Google Gemini, Ollama, OpenRouter (and OpenAI-compatible APIs)
- **Document parsing**: PDF, DOCX, TXT, MD
- **Flexible generation modes**: One row per document, one row per chunk, or multiple rows per chunk
- **Schema validation**: Define dataset format with JSON schema or example
- **Export formats**: JSONL, JSON, CSV
- **Local-first**: API keys stored in OS keyring, no telemetry
- **Resume support**: Automatic checkpoints for interrupted generations
- **Cross-platform**: Windows, macOS, Linux

## Installation

### From source

```bash
# Install with uv
uv sync

# Run the app
uv run answer
```

### From releases

Download the latest release for your platform from [GitHub Releases](https://github.com/Articipate/answer/releases). On macOS, you may need to right-click and open the app if Gatekeeper blocks it (unsigned app). On Windows, SmartScreen may show a warning for unsigned builds.

## Usage

1. **Provider**: Configure your AI provider and API key
2. **Documents**: Add your source documents
3. **Format**: Define your dataset schema/format
4. **Generate**: Generate and review dataset rows, then export

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linter
uv run ruff check src tests
```

## Building

We use [cx_Freeze](https://cx-freeze.readthedocs.io/) to build distributable packages. Builds are done natively on each platform via GitHub Actions.

```bash
# Build locally (platform-specific)
python packaging/cxfreeze/setup.py build_exe
```

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Articipate
