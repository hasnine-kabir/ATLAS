"""CLI entry point for ATLAS: py -3.11 -m atlas."""

import argparse
import sys

from atlas import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ATLAS CLI."""
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="ATLAS — JARVIS-style Voice Assistant for Windows 11",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"atlas {__version__}",
        help="Show ATLAS version and exit.",
    )
    parser.add_argument(
        "--repl",
        action="store_true",
        default=False,
        help="Start an interactive text REPL (Slice 1).",
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        default=False,
        help="Start the push-to-talk voice loop (Slice 3).",
    )
    return parser


def _run_repl() -> None:
    """Wire the pipeline and run an interactive text REPL."""
    from pathlib import Path

    from atlas.composer import ResponseComposer
    from atlas.config import load_app_aliases, load_config
    from atlas.nlu.rules import RulesRouter
    from atlas.os_adapter.windows import WindowsOSAdapter
    from atlas.tools.apps import make_open_app_handler
    from atlas.tools.registry import ToolRegistry
    from atlas.tts.fallback import FallbackTTS
    from atlas.tts.piper import PiperTextToSpeech
    from atlas.tts.sapi import SAPITextToSpeech

    config = load_config()
    tts_config = config.get("tts", {})

    # Try Piper, fallback to SAPI
    sapi = SAPITextToSpeech(rate=tts_config.get("rate", 1.0))
    # Fake paths so it falls back to SAPI immediately if missing (which it is)
    try:
        piper = PiperTextToSpeech(Path("models/piper.onnx"), Path("models/piper.json"))
        tts = FallbackTTS(primary=piper, fallback=sapi)
    except Exception:
        # If piper init fails (missing model), just use SAPI as primary fallback
        tts = FallbackTTS(primary=sapi, fallback=sapi)

    composer = ResponseComposer(tts=tts, enabled=tts_config.get("enabled", True))

    aliases = load_app_aliases()
    router = RulesRouter(app_aliases=aliases)

    adapter = WindowsOSAdapter()
    registry = ToolRegistry()
    registry.register("open_app", make_open_app_handler(adapter))

    print(f"ATLAS v{__version__} — text mode. Type 'quit' to exit.\n")
    while True:
        try:
            utterance = input("atlas> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        utterance = utterance.strip()
        if not utterance:
            continue
        if utterance.lower() in ("quit", "exit"):
            print("Goodbye.")
            break

        intent = router.route(utterance)
        if intent is None:
            print("I'm not sure what you mean. Try 'open <app name>'.")
            continue

        result = registry.execute(intent)
        print(result.say)
        composer.handle_result(result)


def _run_voice() -> None:
    """Wire and run the push-to-talk voice loop."""
    import logging

    logging.basicConfig(level=logging.INFO)

    from pathlib import Path

    from atlas.app import AtlasApp
    from atlas.audio.ptt import PushToTalkSource
    from atlas.composer import ResponseComposer
    from atlas.config import load_app_aliases, load_config
    from atlas.nlu.rules import RulesRouter
    from atlas.os_adapter.windows import WindowsOSAdapter
    from atlas.stt.faster_whisper import FasterWhisperSTT
    from atlas.tools.apps import make_open_app_handler
    from atlas.tools.registry import ToolRegistry
    from atlas.tts.fallback import FallbackTTS
    from atlas.tts.piper import PiperTextToSpeech
    from atlas.tts.sapi import SAPITextToSpeech

    config = load_config()
    tts_config = config.get("tts", {})

    sapi = SAPITextToSpeech(rate=tts_config.get("rate", 1.0))
    try:
        piper = PiperTextToSpeech(Path("models/piper.onnx"), Path("models/piper.json"))
        tts = FallbackTTS(primary=piper, fallback=sapi)
    except Exception:
        tts = FallbackTTS(primary=sapi, fallback=sapi)

    composer = ResponseComposer(tts=tts, enabled=tts_config.get("enabled", True))

    aliases = load_app_aliases()
    router = RulesRouter(app_aliases=aliases)

    # Hints from aliases
    hints = list(aliases.keys())

    adapter = WindowsOSAdapter()
    registry = ToolRegistry()
    registry.register("open_app", make_open_app_handler(adapter))

    from atlas.telemetry import JSONTelemetrySink
    
    # Voice specific components
    source = PushToTalkSource(hotkey=config.get("hotkey", "ctrl+space"))
    stt = FasterWhisperSTT(
        model_size=config.get("stt", {}).get("model", "base.en"), device="cpu", compute_type="int8"
    )
    telemetry = JSONTelemetrySink(log_path=Path("logs/performance.jsonl"))

    app = AtlasApp(
        audio_source=source,
        stt=stt,
        router=router,
        registry=registry,
        composer=composer,
        telemetry=telemetry,
        vocabulary_hint=hints,
    )
    app.run_loop()


def main(argv: list[str] | None = None) -> int:
    """Main CLI execution handler."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.voice:
        _run_voice()
        return 0

    if args.repl:
        _run_repl()
        return 0

    # Default behavior — just confirm the install works.
    print(f"ATLAS v{__version__} — ready. Use --help for available options.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
