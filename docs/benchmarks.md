# ATLAS Hardware Profile and Benchmark Results

**Date**: 2026-09-29  
**Machine**: Hasnine's Windows PC  
**Target Environment**: Windows 11, Python 3.11 (64-bit)

---

## 1. Hardware Profile

| Component | Specification |
|---|---|
| **Operating System** | Windows 11 (Build 10.0.26200) |
| **Python Runtime** | 3.11.9 (64-bit) |
| **Processor (CPU)** | AMD Ryzen 5 5600G with Radeon Graphics |
| **Cores** | 6 Physical Cores / 12 Logical Processors |
| **System Memory (RAM)** | 15.9 GB Total (~9.2 GB Available) |
| **Graphics (GPU)** | Intel(R) Arc(TM) A380 Graphics |

---

## 2. Audio Subsystem

| Parameter | Detected Value |
|---|---|
| **Default Input Device (Microphone)** | Microphone (USB Audio Device) [MME] |
| **Default Output Device (Speakers)** | Speakers (USB Audio Device) [MME] |
| **Total Audio Endpoints Detected** | 27 |
| **Sampling Rate Standard** | 16,000 Hz (16 kHz mono PCM) |

---

## 3. Library Verification (CPython 3.11 on Windows win_amd64)

Verification against PyPI wheels and native execution in `.venv`:

| Component | Library | Verified Version | Wheel Type | Status |
|---|---|---|---|---|
| Audio I/O | `sounddevice` | 0.5.6 | `py3-none-win_amd64` (PortAudio bundled) | Verified |
| Audio I/O (Alt) | `PyAudio` | 0.2.14 | `cp311-cp311-win_amd64` | Verified |
| Speech-to-Text | `faster-whisper` | 1.2.1 | `py3-none-any` + `ctranslate2` 4.8.2 wheel | Verified |
| Speech Synthesis | `pyttsx3` (SAPI) | 2.99 | Pure Python Windows SAPI bridge | Verified |
| LLM Provider | `google-genai` | 2.18.1 | `py3-none-any` official SDK | Verified |
| System Metrics | `psutil` | 7.2.2 | `cp37-abi3-win_amd64` | Verified |
| Windows COM / Audio | `comtypes` | 1.4.16 | `py2.py3-none-any` | Verified |
| Safe Recycle | `send2trash` | 1.8.3 | `py3-none-any` | Verified |
| Fuzzy Matching | `rapidfuzz` | 3.10.0+ | `cp311-cp311-win_amd64` | Verified |
| Linting & Formatting | `ruff` | 0.16.9 | `py3-none-win_amd64` (Rust binary) | Verified |
| Type Checking | `mypy` | 2.3.1 | `cp311-cp311-win_amd64` | Verified |
| Test Runner | `pytest` | 9.1.1 | `py3-none-any` | Verified |
| Mutation Testing | `cosmic-ray` | 8.7.0 | `py3-none-any` (Runs natively on Win11) | Verified |

---

## 4. Faster-Whisper Model Benchmark (CPU, int8)

Measured using `scripts/benchmark_hardware.py`:

| Model Size | Quantization | First Load Time | Inference Latency (Median) | Target Budget | Status |
|---|---|---|---|---|---|
| `base.en` | `int8` | 17.65s (incl. HF download) | ~7.4s (cold) | < 800 ms | Baseline |
| `small.en` | `int8` | 47.14s (incl. HF download) | 1,352.3 ms (warm) | < 800 ms | Viable with acceleration |

*Notes*:
- On CPU int8, warm inference for `small.en` achieves ~1.35 seconds.
- The machine is equipped with a dedicated **Intel Arc A380 GPU**. OpenVINO / DirectX execution providers can be leveraged to bring `small.en` under the 500ms target during Slice 4.

---

## 5. Architectural Decisions Record (Slice 0)

### Decision D1: Wake Word Engine
- **Decision**: `openWakeWord` with custom "atlas" model; fallback to transcript-match on VAD.
- **Rationale**: Local, zero cloud dependency, no proprietary API keys required.

### Decision D2: Text-to-Speech Engine
- **Decision**: Piper ONNX voice (`en_US-lessac-medium`) as primary, with native Windows SAPI (`pyttsx3`) as zero-dependency fallback.
- **Rationale**: Guarantees audible feedback even without external model files.

### Decision D3: Default Speech-to-Text Model
- **Decision**: Default to `base.en` on CPU; allow configurable switch to `small.en` via `config/atlas.yaml` for higher accuracy when GPU/OpenVINO acceleration is enabled.
- **Rationale**: Maintains fast responsiveness for local voice commands.

### Decision D8: Mutation Testing on Windows
- **Decision**: `cosmic-ray` for native Windows 11 development; `mutmut` documented for WSL2 users.
- **Rationale**: `mutmut` currently requires Linux/WSL2; `cosmic-ray` executes cleanly on native Windows 11.
