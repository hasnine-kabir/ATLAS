# Seed Notes: voice_control.py Audit

**Audit Date**: 2026-09-28  
**Source**: `C:\VoiceControl\voice_control.py` (ARIA Voice Control v9)  
**Target Project**: ATLAS (`feat/atlas-voice-assistant`)

---

## 1. Overview of Seed Code

The seed script `voice_control.py` is a monolithic ~765-line Python script that provided voice control under the name "ARIA". It combined:
- Cloud-based speech recognition via Google Web Speech API (`speech_recognition.Recognizer.recognize_google`)
- Local speech synthesis using Windows SAPI (`pyttsx3`)
- LLM natural language processing and fallback via Google GenAI (`google-genai` SDK)
- Direct OS manipulation via `os.system()`, `pyautogui`, `webbrowser`, and `psutil`
- Sound-level double-clap detection via `pyaudio` and `audioop`

---

## 2. Components to Salvage

The following assets and logic from `voice_control.py` will be carried into ATLAS:

### 2.1 Gemini Auto Model Detection & Fallback Sequence
- **Logic**: Iterating through available Gemini models (`gemini-3.5-flash`, `gemini-3.6-flash`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-flash-latest`) and caching the first working model (`ACTIVE_MODEL`).
- **SDK Usage**: Pinned to the official `google-genai` SDK (`from google import genai; from google.genai import types as genai_types`).
- **Error Handling**: Specific detection of auth/quota/network failures to provide informative feedback.
- **Porting Plan**: Encapsulate inside `src/atlas/llm/gemini.py` behind the `LLMProvider` interface in Slice 12.

### 2.2 App Alias Dictionary (`APP_MAP`)
- **Coverage**: 40+ curated Windows application names, process names, and URI protocols (e.g. `chrome`, `winword`, `excel`, `powerpnt`, `notepad`, `calc`, `taskmgr`, `ms-settings:`, `code`, `pycharm64`, `spotify`, `discord`, `obs64`, `figma`).
- **Porting Plan**: Port into `config/atlas.yaml` under `apps:` so users can customize and extend aliases without touching code.

### 2.3 Website and Folder Mappings (`SITE_MAP` & `FOLDER_MAP`)
- **Coverage**: Pre-mapped URLs for top sites (Google, YouTube, GitHub, Stack Overflow, Reddit, Claude, etc.) and standard user folders (`Desktop`, `Downloads`, `Documents`, `Pictures`, `Music`, `Videos`, `AppData`).
- **Porting Plan**: Port into `config/atlas.yaml` under `sites:` and `files.allowed_roots:`.

### 2.4 Windows OS Commands & Direct Actions
- Safe commands: Screen locking (`rundll32.exe user32.dll,LockWorkStation`), suspend/sleep (`rundll32.exe powrprof.dll,SetSuspendState 0,1,0`), shutdown with abort timer (`shutdown /s /t ...` and `shutdown /a`).
- Metric queries: CPU, RAM, and Disk space queries using `psutil`.
- Porting Plan: Encapsulate into `src/atlas/os_adapter/windows.py` behind the `OSAdapter` interface.

### 2.5 Persona Baseline
- Time-of-day greetings (`tod()` logic: morning, afternoon, evening, night).
- Spoken reply brevity constraint (1-2 sentences).
- Address form (`Hasnine`, configurable).
- Porting Plan: Encapsulate into `src/atlas/persona/phrases.py` and `src/atlas/persona/prompts.py`.

---

## 3. Components Being Replaced or Upgraded

| Feature in `voice_control.py` | Limitation / Vulnerability | ATLAS Architecture |
|---|---|---|
| **Plaintext API Key** | Hardcoded in script (`GEMINI_API_KEY = "..."`) | `.env` file + Windows `keyring` storage; omitted from logs and git |
| **STT Engine** | Google Web Speech (cloud-dependent, latency, privacy leak) | Local `faster-whisper` (`base.en` / `small.en`) running offline |
| **Wake Detection** | Continuous cloud STT / simple energy double-clap | Local `openWakeWord` ("Atlas" model) + Silero VAD endpointing |
| **OS Execution** | Unchecked string execution (`os.system("start " + name)`) | `OSAdapter` with path normalization, sandboxing, and parameter sanitization |
| **File Deletion** | Permanent unrecoverable deletion (`os.remove()`) | `send2trash` (moves to Recycle Bin only) |
| **Action Protocol** | Regex on arbitrary LLM text output (`ACTION:<cmd>:<args>`) | Validated structured tool calls (`ToolSpec`, JSON Schema validation) |
| **Safety Gate** | None: destructive actions (shutdown, delete) run immediately | 3-tier Risk Gate (`SAFE`, `CONFIRM`, `BLOCKED`) with fresh voice confirmation |
| **Concurrency** | Ad-hoc threads and `time.sleep` polling | Asyncio event loop, state machine (`state.py`), decoupled ring buffers |
| **Audio Gate** | Primitive `ARIA_SPEAKING` global boolean flag | Formal state machine (`SPEAKING`, `MUTED`, barge-in support) |
| **TTS Engine** | Windows SAPI only (`pyttsx3`) | High quality local Piper ONNX voice with SAPI fallback |

---

## 4. Migration Plan

1. **Keep `C:\VoiceControl\voice_control.py` intact and runnable** during development.
2. In Phase 1 (Slices 1–4): Port `APP_MAP` into rules router and verify offline app launching and local TTS/STT.
3. In Phase 2 (Slices 5–11): Port OS actions (sleep, volume, windows, files, search) behind `OSAdapter` and `safety/risk.py`.
4. In Phase 3 (Slice 12): Port the Gemini client and auto-model detection into `src/atlas/llm/gemini.py`, reading keys securely from `.env`.
