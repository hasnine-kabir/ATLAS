# ATLAS — JARVIS-style Voice Assistant for Windows 11

ATLAS is a local-first, safety-gated voice assistant for Windows 11. It carries out commands (launching apps, managing windows, volume, media, timers, reminders, file searching) with sub-50ms deterministic local routing and a calm, conversational personality. A cloud LLM (Google Gemini) is invoked only as a fallback for open-ended queries or natural language multi-step commands.

---

## Key Architectural Principles

1. **Local-First & Private**: Wake word detection (`openWakeWord`), speech-to-text (`faster-whisper`), and speech synthesis (`Piper` with Windows SAPI fallback) run 100% locally. Audio never leaves RAM and is never uploaded.
2. **Deterministic Fast Path**: Common system, app, and media commands are recognized offline via rule-based pattern matching in under 50ms without invoking an LLM.
3. **Safety Gate & Confirmation**: Every action has an assigned risk level (`SAFE`, `CONFIRM`, `BLOCKED`). Potentially destructive actions (sleep, shutdown, file deletion, keystroke injection) strictly require a fresh spoken confirmation and are logged to an audit trail.
4. **Ports and Adapters**: Core routing, state machines, and business logic remain completely decoupled from audio devices, operating system calls, and external networks through abstract ports and concrete adapters.

---

## Prerequisites

- **Operating System**: Windows 11 (64-bit)
- **Python**: Python 3.11 pinned (`py -3.11`)
- **Hardware**: Working microphone and speakers / headset; minimum 4GB RAM (8GB+ recommended)

---

## Getting Started

### 1. Clone & Set Up Virtual Environment

```powershell
# Navigate to the repository
cd E:\GITHUB\atlas

# Create Python 3.11 virtual environment
py -3.11 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install in editable mode with development, audio, and platform extras
pip install -e ".[dev,audio,stt,tts,llm,windows]"
```

### 3. Configure Secrets & Settings

```powershell
# Copy example environment configuration
Copy-Item .env.example .env

# Edit .env and supply your Gemini API key:
# GEMINI_API_KEY=your_gemini_api_key_here
```

User settings, aliases, and safety policies are configured in `config/atlas.yaml`.

---

## Verifying the Installation

Check the CLI entry point:

```powershell
py -3.11 -m atlas --version
# Output: atlas 0.1.0
```

Run the hardware profiler and audio device benchmark:

```powershell
python scripts/benchmark_hardware.py
```

---

## Pre-PR Quality Gate

Run the full quality gate before submitting any pull request:

```powershell
# 1. Linting
py -3.11 -m ruff check .

# 2. Code formatting check
py -3.11 -m ruff format --check .

# 3. Strict static type analysis
py -3.11 -m mypy --strict src

# 4. Test suite with line coverage
py -3.11 -m pytest -q --cov=atlas --cov-report=term-missing
```

---

## Mutation Testing

In accordance with the working agreement, test suites must maintain an 80%+ mutation score on core decision modules (`nlu/`, `safety/`, `tools/`).

### Windows Native (Recommended)
ATLAS uses [`cosmic-ray`](https://github.com/sixty-north/cosmic-ray) for native Windows 11 mutation testing:

```powershell
# Initialize mutation session configuration
cosmic-ray init cosmic-ray.toml cosmic-ray.sqlite

# Execute mutation test runs
cosmic-ray exec cosmic-ray.sqlite

# Generate survival and mutation report
cosmic-ray report cosmic-ray.sqlite
```

### WSL2 (Alternative)
For developers running tests within WSL2 (Ubuntu / Debian):

```bash
# Run mutmut across test suite
mutmut run
mutmut results
```

---

## Project Structure

```
atlas/
├── pyproject.toml              # Build config, dependencies, linter/type settings
├── README.md                   # Project documentation and developer guide
├── .env.example                # Template for environment secrets
├── config/
│   └── atlas.yaml              # User preferences, app aliases, safety policies
├── docs/
│   ├── seed-notes.md           # Audit of legacy voice_control.py seed code
│   └── benchmarks.md           # Hardware profile and latency benchmark results
├── scripts/
│   └── benchmark_hardware.py   # System profile and faster-whisper benchmark
├── src/atlas/
│   ├── __init__.py             # Package init & version
│   ├── __main__.py             # CLI entry point (py -3.11 -m atlas)
│   ├── app.py                  # Composition root wiring ports to adapters
│   ├── audio/                  # Audio I/O, VAD, ring buffers, wake word
│   ├── llm/                    # Gemini provider and fallback router
│   ├── memory/                 # SQLite storage for persistent reminders and notes
│   ├── nlu/                    # Normalization, rules router, intent resolution
│   ├── os_adapter/             # Windows native OS actions and test fakes
│   ├── persona/                # Prompts, responses, and phrase variation
│   ├── safety/                 # Risk gating, voice confirmation, audit trail
│   ├── stt/                    # Local speech-to-text (faster-whisper)
│   ├── tools/                  # Tool catalogue and handlers
│   └── tts/                    # Local text-to-speech (Piper / SAPI)
└── tests/
    ├── unit/                   # Pure logic unit tests
    ├── component/              # State machine and wiring tests with fakes
    ├── integration/            # Real Windows OS API tests (@pytest.mark.windows)
    └── acceptance/             # End-to-end audio pipeline tests
```

---

## License

Private repository — Hasnine Kabir.
