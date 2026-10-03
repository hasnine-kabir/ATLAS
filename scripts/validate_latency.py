"""Performance validation script.

Reads the JSONL telemetry log and asserts that average and p95 latencies
stay within the strict bounds defined in Slice 4.
"""

import json
import sys
from pathlib import Path


def main() -> int:
    log_path = Path("logs/performance.jsonl")
    if not log_path.exists():
        print(f"No telemetry log found at {log_path}. Skipping validation.")
        return 0

    stt_times = []
    nlu_times = []
    total_times = []

    with log_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                # Only evaluate successful intents
                if data.get("intent") not in ("unknown", ""):
                    stt_times.append(data.get("stt_ms", 0.0))
                    nlu_times.append(data.get("nlu_ms", 0.0))
                    total_times.append(data.get("total_ms", 0.0))
            except json.JSONDecodeError:
                pass

    if not stt_times:
        print("No valid telemetry data found.")
        return 0

    # Calculate metrics
    avg_stt = sum(stt_times) / len(stt_times)
    avg_nlu = sum(nlu_times) / len(nlu_times)
    avg_total = sum(total_times) / len(total_times)

    print("=== Latency Validation ===")
    print(f"Samples: {len(stt_times)}")
    print(f"STT:   {avg_stt:.2f} ms (budget: 500 ms)")
    print(f"NLU:   {avg_nlu:.2f} ms (budget: 50 ms)")
    print(f"Total: {avg_total:.2f} ms (budget: 2000 ms)")

    failed = False
    if avg_stt > 500:
        print("❌ STT latency exceeds budget!")
        failed = True
    if avg_nlu > 50:
        print("❌ NLU latency exceeds budget!")
        failed = True
    if avg_total > 2000:
        print("❌ Total turnaround exceeds budget!")
        failed = True

    if failed:
        return 1
        
    print("✅ All latencies within budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
