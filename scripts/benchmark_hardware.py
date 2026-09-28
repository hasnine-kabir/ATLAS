"""Hardware and Audio Benchmark Script for ATLAS.

Gathers hardware profile (CPU, GPU, RAM, OS build), enumerates audio devices,
and benchmarks faster-whisper (base.en and small.en) to resolve Decision D3.
"""

from __future__ import annotations

import math
import platform
import struct
import subprocess
import sys
import time
import wave
from pathlib import Path
from typing import Any

import psutil


def get_cpu_name() -> str:
    """Get the full CPU brand string on Windows."""
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
        )
        name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
        return str(name).strip()
    except Exception:
        return platform.processor() or "Unknown CPU"


def get_gpu_info() -> list[str]:
    """Get video controllers via PowerShell CIM instance."""
    try:
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        return lines if lines else ["None detected"]
    except Exception as exc:
        return [f"Detection error: {exc}"]


def get_audio_devices() -> tuple[list[dict[str, Any]], str, str]:
    """Enumerate audio input and output devices using sounddevice if available."""
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        device_list: list[dict[str, Any]] = []
        default_in = ""
        default_out = ""

        def_in_idx, def_out_idx = sd.default.device

        for idx, dev in enumerate(devices):
            hostapi_name = (
                hostapis[dev["hostapi"]]["name"] if dev.get("hostapi") is not None else ""
            )
            info = {
                "index": idx,
                "name": dev["name"],
                "hostapi": hostapi_name,
                "inputs": dev["max_input_channels"],
                "outputs": dev["max_output_channels"],
                "sample_rate": dev["default_samplerate"],
            }
            device_list.append(info)
            if idx == def_in_idx:
                default_in = f"[{idx}] {dev['name']} ({hostapi_name})"
            if idx == def_out_idx:
                default_out = f"[{idx}] {dev['name']} ({hostapi_name})"

        return device_list, default_in, default_out
    except Exception as exc:
        return [{"error": str(exc)}], "Unavailable", "Unavailable"


def generate_sample_wav(target_path: Path, duration_s: float = 2.0) -> None:
    """Generate a clean synthetic WAV file for benchmark consistency."""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_s)
    # Generate a dual-frequency pleasant tone (440Hz + 880Hz)
    raw_data = bytearray()
    for i in range(num_samples):
        t = float(i) / sample_rate
        val = 0.4 * math.sin(2.0 * math.pi * 440.0 * t) + 0.2 * math.sin(2.0 * math.pi * 880.0 * t)
        sample = int(val * 32767.0)
        raw_data.extend(struct.pack("<h", max(-32768, min(32767, sample))))

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(target_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(raw_data)


def benchmark_whisper_model(model_name: str, wav_path: Path) -> dict[str, Any]:
    """Benchmark model load time and inference latency on CPU with int8 quantization."""
    try:
        from faster_whisper import WhisperModel

        t0 = time.perf_counter()
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        load_time_s = time.perf_counter() - t0

        # Run 3 inference passes and take the median
        latencies: list[float] = []
        transcript = ""
        for _ in range(3):
            t_start = time.perf_counter()
            segments, _ = model.transcribe(str(wav_path), beam_size=1, language="en")
            transcript = " ".join(s.text.strip() for s in segments)
            latencies.append(time.perf_counter() - t_start)

        latencies.sort()
        median_latency_ms = latencies[len(latencies) // 2] * 1000.0

        return {
            "model": model_name,
            "load_time_s": round(load_time_s, 2),
            "median_latency_ms": round(median_latency_ms, 1),
            "sample_transcript": transcript,
            "status": "ok",
        }
    except Exception as exc:
        return {
            "model": model_name,
            "error": str(exc),
            "status": "failed",
        }


def run_benchmark() -> dict[str, Any]:
    """Execute complete hardware benchmark."""
    print("=" * 60)
    print("ATLAS Hardware Profile & Benchmark")
    print("=" * 60)

    # 1. OS & System
    os_name = f"{platform.system()} {platform.release()} (Build {platform.version()})"
    cpu_name = get_cpu_name()
    logical_cores = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)
    ram = psutil.virtual_memory()
    total_ram_gb = round(ram.total / (1024**3), 2)
    avail_ram_gb = round(ram.available / (1024**3), 2)
    gpus = get_gpu_info()

    print(f"OS:            {os_name}")
    print(f"Python:        {sys.version.split()[0]} ({platform.architecture()[0]})")
    print(f"CPU:           {cpu_name}")
    print(f"Cores:         {physical_cores} physical / {logical_cores} logical")
    print(f"RAM:           {total_ram_gb} GB total ({avail_ram_gb} GB available)")
    print(f"GPU(s):        {', '.join(gpus)}")

    # 2. Audio devices
    print("\nAudio Subsystem:")
    devices, def_in, def_out = get_audio_devices()
    print(f"Default Input (Mic):   {def_in}")
    print(f"Default Output (Spk):  {def_out}")
    print(f"Total Audio Endpoints: {len(devices)}")

    # 3. Whisper Benchmark
    sample_wav = Path(".benchmark_tmp") / "test_tone.wav"
    generate_sample_wav(sample_wav, duration_s=2.0)

    print("\nBenchmarking faster-whisper models (CPU, int8)...")
    base_res = benchmark_whisper_model("base.en", sample_wav)
    print(
        f" -> base.en:  Load {base_res.get('load_time_s', 'err')}s | Median Latency: {base_res.get('median_latency_ms', 'err')} ms"
    )

    small_res = benchmark_whisper_model("small.en", sample_wav)
    print(
        f" -> small.en: Load {small_res.get('load_time_s', 'err')}s | Median Latency: {small_res.get('median_latency_ms', 'err')} ms"
    )

    if sample_wav.exists():
        try:
            sample_wav.unlink()
            sample_wav.parent.rmdir()
        except Exception:
            pass

    # Recommendation
    target_budget_ms = 800.0
    recommended_model = "small.en"
    if (
        small_res.get("status") == "ok"
        and small_res.get("median_latency_ms", 9999) <= target_budget_ms
    ):
        recommended_model = "small.en"
        rec_reason = f"Latency ({small_res['median_latency_ms']} ms) is well within the {target_budget_ms} ms budget."
    elif base_res.get("status") == "ok":
        recommended_model = "base.en"
        rec_reason = "small.en exceeded latency budget or failed; falling back to base.en."
    else:
        recommended_model = "base.en"
        rec_reason = "Fallback default."

    print(f"\nRecommended Model (Decision D3): {recommended_model}")
    print(f"Reason: {rec_reason}")
    print("=" * 60)

    return {
        "os": os_name,
        "cpu": cpu_name,
        "cores": f"{physical_cores}p / {logical_cores}l",
        "ram_gb": total_ram_gb,
        "gpus": gpus,
        "default_input": def_in,
        "default_output": def_out,
        "whisper_base": base_res,
        "whisper_small": small_res,
        "recommended_model": recommended_model,
    }


if __name__ == "__main__":
    run_benchmark()
